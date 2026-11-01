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
    for folder in sorted((ROOT / 'results').iterdir()):
        if not folder.is_dir() or not (folder / 'metadata.json').exists():
            continue
        meta = json.loads((folder / 'metadata.json').read_text())
        records = [json.loads(line) for line in (folder / 'records.jsonl').read_text().splitlines()]
        assert all(r['method'] in METHODS for r in records)
        assert len({(r['map_id'], r['method']) for r in records}) == len(records)
        for method in dict.fromkeys(r['method'] for r in records):
            selected = [r for r in records if r['method'] == method]
            solved = [r for r in selected if r['solved']]
            exp = [r['expansions'] for r in solved]
            costs = [r.get('cost') for r in solved]
            mean = lambda v: float(np.mean(v)) if v else None
            row = {'run': folder.name, 'method': method, 'algorithm': METHODS[method],
                   'hardware': meta['hardware'], 'timeout_sec': meta['timeout_sec'],
                   'max_expansions': meta.get('classical_max_expansions', meta['max_expansions']) if method == 'classical_astar' else meta['max_expansions'],
                   'evaluated': len(selected), 'solved': len(solved),
                   'mean_expansions': mean(exp), 'median_expansions': float(np.median(exp)) if exp else None,
                   'p90_expansions': float(np.percentile(exp, 90)) if exp else None,
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

The seven-box evaluation is an **82/100 snapshot**: maps 1–45 have archived raw
records; maps 46–82 are completed live-log records whose action plans and costs
were not exported at the reporting cutoff. Its Paper Learned GBFS row covers
only maps 1–5 and must not be interpreted as an 82-map solve rate. Later maps
are outside this report. Method names retain historical terminology; checkpoint
identity as a published paper model is not verified.
'''
    for boxes in [3, 5, 7]:
        md += f'\n## {boxes}-box Sokoban — {"IID" if boxes == 3 else "OOD"}\n\n'
        md += '| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost |\n'
        md += '|---|---|---|---:|---:|---:|---:|---:|\n'
        for r in sorted(rows[boxes], key=lambda r: (list(METHODS).index(r['method']), r['hardware'])):
            vals = ['—' if r[k] is None else f'{r[k]:,.1f}' for k in ('mean_expansions', 'median_expansions', 'p90_expansions', 'mean_cost')]
            md += f'| {r["algorithm"]} | {r["hardware"]} | {r["timeout_sec"]:g} / {r["max_expansions"]:,} | {r["solved"]}/{r["evaluated"]} ({100*r["solved"]/r["evaluated"]:.1f}%) | ' + ' | '.join(vals) + ' |\n'
    md += '\n## Paired comparisons within recorded runs\n\n'
    for p in paired:
        md += f'- `{p["run"]}`: {METHODS[p["method"]]} vs {METHODS[p["baseline"]]}: N={p["common"]}; {p["wins"]}W/{p["ties"]}T/{p["losses"]}L; mean expansion reduction {p["mean_reduction_pct"]:.2f}% (negative means more expansions).\n'
    md += '\n## Limitations\n\nMC dropout is model-dependent: scratch M0 solves 93/100 five-box maps versus 77/100 for its MC variant, and 65/82 seven-box maps versus 53/82. Inference-time perturbation sensitivity, altered rankings and gating interactions are hypotheses, not demonstrated causes. Disagreement has not been established as a calibrated predictor of distance error. These learned search methods do not guarantee optimal plans. “Calibrated” names a gating configuration, not statistical error calibration.\n'
    (ROOT / 'RESULTS.md').write_text(md, encoding='utf-8')
    (ROOT / 'results/summary.json').write_text(json.dumps({'tables': rows, 'paired': paired}, indent=2), encoding='utf-8')
    print('Saved RESULTS.md; table rows:', {b: len(r) for b, r in rows.items()})
    return rows


if __name__ == '__main__':
    build()
