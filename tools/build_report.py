"""Build three domain tables from the retained per-map evidence."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import replay_plan


def build():
    rows = {3: [], 5: [], 7: []}
    grouped = {}
    partial = []
    for folder in sorted((ROOT / 'results').iterdir()):
        if not folder.is_dir() or not (folder / 'metadata.json').exists():
            continue
        meta = json.loads((folder / 'metadata.json').read_text())
        records = [json.loads(line) for line in (folder / 'records.jsonl').read_text().splitlines()]
        assert all(r['method'] in METHODS for r in records)
        assert len({(r['map_id'], r['method']) for r in records}) == len(records)
        if meta.get('partial'):
            partial.extend(records)
            continue
        for method in dict.fromkeys(r['method'] for r in records):
            selected = [r for r in records if r['method'] == method]
            solved = [r for r in selected if r['solved']]
            exp = [r['expansions'] for r in solved]
            costs = [r.get('cost') for r in solved]
            wall_times = [r.get('wall_time_sec') for r in selected]
            search_times = [r['time_sec'] for r in selected]
            assert all(np.isfinite(v) and v >= 0 for v in search_times)
            has_dispatch_times = all(v is not None for v in wall_times)
            mean = lambda v: float(np.mean(v)) if v else None
            row = {'run': folder.name, 'method': method, 'algorithm': METHODS[method],
                   'hardware': meta['hardware'], 'timeout_sec': meta['timeout_sec'],
                   'max_expansions': meta.get('classical_max_expansions', meta['max_expansions']) if method == 'classical_astar' else meta['max_expansions'],
                   'evaluated': len(selected), 'solved': len(solved),
                   'mean_expansions': mean(exp), 'median_expansions': float(np.median(exp)) if exp else None,
                   'p90_expansions': float(np.percentile(exp, 90)) if exp else None,
                   'mean_search_time_sec': mean(search_times),
                   'mean_elapsed_time_sec': mean(wall_times if has_dispatch_times else search_times),
                   'timing_scope': 'including_dispatch_setup' if has_dispatch_times else 'search_only',
                   'mean_wall_time_sec': mean(wall_times) if all(v is not None for v in wall_times) else None,
                   'mean_cost': mean(costs) if costs and all(c is not None for c in costs) else None}
            rows[meta['boxes']].append(row)
            grouped[folder.name, method] = selected
    paired = []
    for run in [p.name for p in (ROOT / 'results').iterdir() if p.is_dir()]:
        for method, base in [('paper_mc_astar', 'paper_astar'), ('single_mc_astar', 'single_astar'),
                             ('ensemble_risk', 'ensemble_conf_020'), ('ensemble_risk', 'ensemble_conf_050')]:
            a = {r['map_id']: r for r in grouped.get((run, method), []) if r['solved']}
            b = {r['map_id']: r for r in grouped.get((run, base), []) if r['solved']}
            shared = sorted(a.keys() & b.keys())
            if not shared:
                continue
            x, y = [a[i]['expansions'] for i in shared], [b[i]['expansions'] for i in shared]
            paired.append({'run': run, 'method': method, 'baseline': base, 'common': len(shared),
                           'wins': sum(u < v for u, v in zip(x, y)), 'ties': sum(u == v for u, v in zip(x, y)),
                           'losses': sum(u > v for u, v in zip(x, y)),
                           'mean_reduction_pct': 100 * (1 - float(np.mean(x)) / float(np.mean(y)))})
    md = '''# Sokoban experiment results

Only the ten methods in `src/methods.py` are supported. Tables retain recorded
hardware and budgets; historical groups are not one controlled cross-device
comparison. Expansions and costs use solved maps. Compare expansions on mutually
solved maps for a paired claim. Unperformed combinations are not invented.
The last column is mean elapsed wall-clock seconds across **all attempts,
including failures**. **S** = search-only elapsed time (historical 3/5-box runs);
**D** = elapsed time including dispatch setup (7-box runs). These scopes differ:
S does not measure the full invocation. Neither includes one-time model loading
or dataset generation. The JSON summary preserves both measurements separately
where available. Hardware and budgets must also be considered when comparing times.

The seven-box comparison uses **94/100 fixed maps**, with archived raw records
and independently replayed successful plans throughout. The completed Kaggle
session stopped partway through map 95; its three completed attempts are listed
separately and excluded from the common-cohort table and paired comparisons.
Paper Learned GBFS covers only maps 1–5, not the 94-map cohort. Method names
retain historical terminology; checkpoint identity as a published paper model
is not verified.
'''
    for boxes in [3, 5, 7]:
        md += f'\n## {boxes}-box Sokoban — {"IID" if boxes == 3 else "OOD"}\n\n'
        md += '| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost | Mean elapsed wall time (s) |\n'
        md += '|---|---|---|---:|---:|---:|---:|---:|---:|\n'
        for r in sorted(rows[boxes], key=lambda r: (list(METHODS).index(r['method']), r['hardware'])):
            vals = ['—' if r[k] is None else f'{r[k]:,.1f}' for k in ('mean_expansions', 'median_expansions', 'p90_expansions', 'mean_cost')]
            marker = 'D' if r['timing_scope'] == 'including_dispatch_setup' else 'S'
            vals.append(f"{r['mean_elapsed_time_sec']:,.2f} {marker}")
            md += f'| {r["algorithm"]} | {r["hardware"]} | {r["timeout_sec"]:g} / {r["max_expansions"]:,} | {r["solved"]}/{r["evaluated"]} ({100*r["solved"]/r["evaluated"]:.1f}%) | ' + ' | '.join(vals) + ' |\n'
    md += '\n## Partial map 95 — excluded from the 94-map comparison\n\n'
    md += '| Method | Solved | Expansions | Search time (s) | Cost | Wall time (s) |\n|---|---|---:|---:|---:|---:|\n'
    for r in partial:
        cost = '—' if r.get('cost') is None else f"{r['cost']:g}"
        md += f"| {METHODS[r['method']]} | {r['solved']} | {r['expansions']:,} | {r['time_sec']:.2f} | {cost} | {r['wall_time_sec']:.2f} |\n"
    md += '\nOther methods did not finish map 95; missing attempts are not failures. Fixed 50/50 Hybrid A* has no seven-box results.\n'
    md += '\n## Paired comparisons within recorded runs\n\n'
    for p in paired:
        md += f'- `{p["run"]}`: {METHODS[p["method"]]} vs {METHODS[p["baseline"]]}: N={p["common"]}; {p["wins"]}W/{p["ties"]}T/{p["losses"]}L; mean expansion reduction {p["mean_reduction_pct"]:.2f}% (negative means more expansions).\n'
    md += '\n## Limitations\n\nMC dropout is model-dependent: scratch M0 solves 93/100 five-box maps versus 77/100 for its MC variant, and also solves more seven-box maps than its MC variant (see the table). Inference-time perturbation sensitivity, altered rankings and gating interactions are hypotheses, not demonstrated causes. Disagreement has not been established as a calibrated predictor of distance error. These learned search methods do not guarantee optimal plans. “Calibrated” names a gating configuration, not statistical error calibration.\n'
    (ROOT / 'RESULTS.md').write_text(md, encoding='utf-8')
    (ROOT / 'results/summary.json').write_text(json.dumps({'tables': rows, 'paired': paired, 'partial_map95': partial}, indent=2), encoding='utf-8')
    print('Saved RESULTS.md; table rows:', {b: len(r) for b, r in rows.items()})
    return rows


if __name__ == '__main__':
    build()
