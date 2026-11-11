"""Verify included assets, saved five-map solutions, and all ten search methods."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import read_boards, replay_plan, sha256
from benchmarks.run_benchmark import run
from tools.report_run import summarize


def check(device='cpu', threads=2):
    hashes = json.loads((ROOT / 'data/assets_sha256.json').read_text(encoding='utf-8'))
    for name, expected in hashes.items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f'Asset checksum mismatch: {name}')
    print(f'PASS: {len(hashes)} asset checksums', flush=True)
    boards = read_boards(ROOT / 'data/sokoban_7box_original_test.txt')
    print(f'PASS: {len(boards)} unique, validated seven-box maps', flush=True)
    records = [json.loads(s) for s in (ROOT / 'results/ood_7box_snapshot94/records.jsonl').read_text(encoding='utf-8').splitlines()]
    first_five = [r for r in records if r['map_id'] <= 5]
    count = 0
    if {r['map_id'] for r in first_five} != set(range(1, 6)):
        raise ValueError('Missing archived evidence for the first five maps')
    for row in first_five:
        if row['method'] not in METHODS:
            raise ValueError('Unsupported method in saved evidence')
        if row['solved']:
            if row['cost'] != len(row['actions']) or not replay_plan(boards[row['map_id'] - 1], row['actions']):
                raise ValueError(f"Saved solution replay failed: map {row['map_id']}, {row['method']}")
            count += 1
    print(f'PASS: {count} saved successful plans replayed on seven-box maps 1-5', flush=True)
    base = ROOT / 'output'
    base.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = Path(tempfile.mkdtemp(prefix=f'sanity_{stamp}_', dir=base))
    run(SimpleNamespace(device=device, threads=threads, smoke_test=True, boxes=7,
                        start_map=1, end_map=1, methods=list(METHODS), profile='uniform',
                        seed=42, output=out, wall_hours=1.0))
    result = summarize(out, expected_maps=1, require_all_methods=True)
    if result['record_count'] != 10 or any(r['solved'] != 1 for r in result['tables']):
        raise ValueError('Every method must solve and replay the one-push validation puzzle')
    print('PASS: all 10 methods solved and replayed the one-push validation puzzle', flush=True)
    print(f'Sanity check PASS. Outputs: {out}', flush=True)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--threads', type=int, default=2)
    args = parser.parse_args()
    if args.threads < 1:
        parser.error('threads must be positive')
    check(args.device, args.threads)
