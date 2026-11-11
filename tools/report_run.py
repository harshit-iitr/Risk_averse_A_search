"""Validate and summarize a run produced by benchmarks/run_benchmark.py."""
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, median
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import fingerprint, replay_plan, sha256, smoke_board
from src.sokoban_env import SokobanEnv


def summarize(run_dir, expected_maps=None, require_all_methods=False):
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / 'metadata.json').read_text(encoding='utf-8'))
    if meta.get('kind') not in ('evaluation', 'smoke_validation'):
        raise ValueError('Use this tool for new runner outputs; archived results use tools/build_report.py')
    methods = meta['methods']
    if not methods or len(set(methods)) != len(methods) or any(m not in METHODS for m in methods):
        raise ValueError('Invalid method selection in metadata')
    if require_all_methods and set(methods) != set(METHODS):
        raise ValueError('The run does not select all ten methods')
    if meta['kind'] == 'smoke_validation':
        boards = [smoke_board()]
    else:
        names = {3: 'sokoban_3box_test.txt', 5: 'sokoban_5box_test.txt', 7: 'sokoban_7box_original_test.txt'}
        dataset = ROOT / 'data' / names[meta['boxes']]
        if sha256(dataset) != meta['dataset_sha256']:
            raise ValueError('Dataset hash differs from the run metadata')
        boards = SokobanEnv.load_dataset(dataset)
        boards = boards[:200 if meta['boxes'] == 3 else 100]
    path = run_dir / 'records.jsonl'
    raw = path.read_text(encoding='utf-8') if path.exists() else ''
    if raw and not raw.endswith('\n'):
        raise ValueError('An attempt is still being written; retry after the record completes')
    records = [json.loads(line) for line in raw.splitlines()]
    seen = set()
    for row in records:
        key = row['map_id'], row['method']
        if (key in seen or row['method'] not in methods or
                not isinstance(row['map_id'], int) or not 1 <= row['map_id'] <= len(boards) or
                row['run_fingerprint'] != fingerprint(meta)):
            raise ValueError('Invalid, duplicate, or mismatched result record')
        if not math.isfinite(row['time_sec']) or row['time_sec'] < 0 or row['expansions'] < 0:
            raise ValueError('Invalid timing or expansion count')
        wall = row.get('wall_time_sec')
        if wall is not None and (not math.isfinite(wall) or wall < 0):
            raise ValueError('Invalid elapsed time')
        if row['solved']:
            if (not row['verified'] or row['cost'] != len(row['actions']) or
                    not replay_plan(boards[row['map_id'] - 1], row['actions'])):
                raise ValueError(f'Solution replay failed: {key}')
        seen.add(key)
    maps = sorted({r['map_id'] for r in records})
    wanted_maps = meta.get('requested_maps', maps)
    if expected_maps is not None:
        if expected_maps < 1:
            raise ValueError('expected-maps must be positive')
        if len(wanted_maps) != expected_maps:
            raise ValueError(f'Expected {expected_maps} maps, found {len(wanted_maps)} in the run')
    expected = {(i, m) for i in wanted_maps for m in methods}
    if not seen <= expected:
        raise ValueError('Result map IDs lie outside the requested range')
    missing = sorted(expected - seen)
    rows = []
    for method in methods:
        attempts = [r for r in records if r['method'] == method]
        solved = [r for r in attempts if r['solved']]
        walls = [r.get('wall_time_sec') for r in attempts]
        rows.append({'method': method, 'algorithm': METHODS[method],
                     'attempted': len(attempts), 'solved': len(solved),
                     'solve_pct': 100 * len(solved) / len(attempts) if attempts else None,
                     'mean_expansions': mean(r['expansions'] for r in solved) if solved else None,
                     'median_expansions': median(r['expansions'] for r in solved) if solved else None,
                     'mean_cost': mean(r['cost'] for r in solved) if solved else None,
                     'mean_search_time_sec': mean(r['time_sec'] for r in attempts) if attempts else None,
                     'mean_wall_time_sec': mean(walls) if walls and all(v is not None for v in walls) else None})
    result = {'kind': meta['kind'], 'boxes': meta['boxes'], 'hardware': meta['hardware'],
              'record_count': len(records), 'expected_attempts': len(expected),
              'complete': not missing, 'missing_attempts': missing, 'tables': rows}
    (run_dir / 'summary.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    with (run_dir / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    label = 'One-push installation check' if meta['kind'] == 'smoke_validation' else f"{meta['boxes']}-box Sokoban evaluation"
    md = f"# {label}\n\nDevice: {meta['hardware']}. Attempts: {len(records)}/{len(expected)}. Status: {'complete' if not missing else 'in progress'}.\n\n"
    md += 'Expansions and costs use solved puzzles. Mean timings include every attempt, including failures. Wall time includes dispatch setup.\n\n'
    md += '| Method | Solved / attempted | Mean exp. | Median exp. | Mean cost | Mean search (s) | Mean wall (s) |\n'
    md += '|---|---:|---:|---:|---:|---:|---:|\n'
    for row in rows:
        def fmt(key):
            return '—' if row[key] is None else f'{row[key]:,.2f}'
        md += f"| {row['algorithm']} | {row['solved']}/{row['attempted']} | "
        md += ' | '.join(fmt(k) for k in ['mean_expansions', 'median_expansions', 'mean_cost', 'mean_search_time_sec', 'mean_wall_time_sec']) + ' |\n'
    (run_dir / 'report.md').write_text(md, encoding='utf-8')
    if expected_maps is not None and missing:
        raise ValueError(f'Incomplete grid: {len(missing)} attempts remain. Interim report saved.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--expected-maps', type=int)
    parser.add_argument('--require-all-methods', action='store_true')
    args = parser.parse_args()
    try:
        result = summarize(args.run_dir, args.expected_maps, args.require_all_methods)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Run validation failed: {exc}\n')
    print(f"Saved report.md, summary.csv and summary.json: {result['record_count']}/{result['expected_attempts']} attempts")
