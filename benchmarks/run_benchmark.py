"""Run the selected Sokoban methods with explicit budgets and replayable results."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import sys
import time

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import sha256, fingerprint, replay_plan, smoke_board
from src.sokoban_env import SokobanEnv
from src.torch_model import ChrestienHeuristicNet
from src.confidence_aware_search import (
    ConfidenceAwareMCHeuristic, run_confidence_aware_astar, run_fixed_hybrid_astar,
    get_device, get_device_name, author_state_to_tensor,
)
from src.ensemble_search import DeepEnsembleHeuristic, run_ensemble_astar
from src.single_search import run_single_scratch_astar
from src import search_iid, search_ood

DATASETS = {3: 'sokoban_3box_test.txt', 5: 'sokoban_5box_test.txt', 7: 'sokoban_7box_original_test.txt'}
CHECKPOINTS = ['finalSok3_pytorch.pt'] + [f'checkpoints/ensemble/ensemble_model_{i}.pt' for i in range(5)]


def dispatch(method, state, paper, models, device, boxes, timeout=360.0, cap=1_000_000):
    if method not in METHODS:
        raise ValueError('Unsupported method')
    targets = SokobanEnv.get_box_targets(state)
    goal = SokobanEnv.get_goal_state(state, targets)
    common = dict(max_time=timeout, max_expansions=cap, dim=10)
    paper.eval()
    for model in models:
        model.eval()
    base = search_iid if boxes == 3 else search_ood
    if method == 'classical_astar':
        result = base.run_classical_astar(state, targets, **common)
    elif method in ('paper_astar', 'paper_gbfs', 'single_astar'):
        tensor = torch.from_numpy(author_state_to_tensor(goal, targets, 10)).unsqueeze(0).to(device)
        if method == 'single_astar':
            result = run_single_scratch_astar(state, targets, models[0], tensor, device, **common)
        else:
            result = base.run_batched_paper_search(state, targets, paper, tensor, device,
                                                  alg='gbfs' if method == 'paper_gbfs' else 'astar', **common)
    elif method in ('paper_mc_astar', 'single_mc_astar', 'fixed_hybrid_astar'):
        heuristic = ConfidenceAwareMCHeuristic(
            models[0] if method == 'single_mc_astar' else paper,
            goal, targets, device, num_mc_samples=5, dropout_p=0.10,
            lambda_min=0.20, scale_constant_C=50.0, dim=10)
        if method == 'fixed_hybrid_astar':
            result = run_fixed_hybrid_astar(state, targets, heuristic, fixed_lambda=0.50, **common)
        else:
            result = run_confidence_aware_astar(state, targets, heuristic, **common)
    else:
        heuristic = DeepEnsembleHeuristic(
            models=models, goal_state=goal, box_targets=targets, device=device,
            lambda_min=0.20 if method == 'ensemble_conf_020' else 0.50,
            beta=2.5, search_mode='risk_averse' if method == 'ensemble_risk' else 'convex',
            kappa=1.0, scale_constant_C=50.0, dim=10)
        result = run_ensemble_astar(state, targets, heuristic, **common)
    return tuple(result[:5]) + (result[5] if len(result) == 6 else {},)


def budget(boxes, method, profile):
    if profile == 'uniform':
        return 360.0, 1_000_000
    if boxes == 7:
        raise ValueError('Seven-box experiments use the uniform profile')
    if method in ('single_astar', 'single_mc_astar', 'ensemble_conf_020', 'ensemble_conf_050', 'ensemble_risk'):
        return 360.0, 1_000_000
    return (600.0, 100_000) if boxes == 3 else (600.0, 150_000 if method == 'classical_astar' else 15_000)


def run(args):
    device = get_device(args.device)
    if args.smoke_test:
        boards = [smoke_board()]
    else:
        boards = SokobanEnv.load_dataset(ROOT / 'data' / DATASETS[args.boxes])
        boards = boards[:200 if args.boxes == 3 else 100]
        for board in boards:
            if np.count_nonzero(board == 4) != args.boxes or np.count_nonzero(board == 2) != args.boxes or np.count_nonzero(board == 3) != 1:
                raise ValueError('Invalid board tile counts')
    end = args.end_map or len(boards)
    if not 1 <= args.start_map <= end <= len(boards):
        raise ValueError('Invalid map range')
    methods = args.methods or list(METHODS)
    if len(set(methods)) != len(methods):
        raise ValueError('Duplicate method selection')
    checkpoints = {p: sha256(ROOT / p) for p in CHECKPOINTS}
    meta = {'boxes': args.boxes, 'kind': 'smoke_validation' if args.smoke_test else 'evaluation',
            'methods': methods, 'profile': args.profile, 'seed': args.seed,
            'hardware': get_device_name(device), 'python': sys.version.split()[0],
            'torch': torch.__version__, 'numpy': np.__version__,
            'checkpoints': checkpoints, 'source_sha256': {str(p.relative_to(ROOT)): sha256(p) for folder in ['src', 'benchmarks'] for p in (ROOT / folder).glob('*.py')},
            'dataset_sha256': None if args.smoke_test else sha256(ROOT / 'data' / DATASETS[args.boxes]),
            'budgets': {m: [10.0, 100] if args.smoke_test else list(budget(args.boxes, m, args.profile)) for m in methods}}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    lock = out / '.run.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    try:
        mp, rp = out / 'metadata.json', out / 'records.jsonl'
        if mp.exists() and json.loads(mp.read_text()) != meta:
            raise ValueError('Resume metadata differs: code/data/models/device/profile/seed changed')
        if not mp.exists():
            if rp.exists():
                raise ValueError('Results exist without metadata')
            mp.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        raw = rp.read_text() if rp.exists() else ''
        if raw and not raw.endswith('\n'):
            raise ValueError('Incomplete final result record; preserve and repair before resuming')
        previous = [json.loads(line) for line in raw.splitlines()]
        done = set()
        for row in previous:
            key = row['map_id'], row['method']
            if key in done or row['run_fingerprint'] != fingerprint(meta):
                raise ValueError('Invalid or duplicate resume record')
            if row['solved'] and not replay_plan(boards[row['map_id'] - 1], row['actions']):
                raise ValueError('Saved plan replay failed')
            done.add(key)
        pending = [(i, m) for i in range(args.start_map, end + 1) for m in methods if (i, m) not in done]
        if not pending:
            print('No pending attempts', flush=True)
            return
        loaded = []
        for name in CHECKPOINTS:
            model = ChrestienHeuristicNet(dim=10).to(device)
            model.load_state_dict(torch.load(ROOT / name, map_location=device, weights_only=True), strict=True)
            model.eval()
            loaded.append(model)
        started = time.monotonic()
        with rp.open('a', encoding='utf-8') as f:
            for map_id, method in pending:
                timeout, cap = meta['budgets'][method]
                if time.monotonic() - started + timeout + 15 > args.wall_hours * 3600:
                    break
                seed = int(fingerprint([args.seed, map_id, method])[:8], 16)
                random.seed(seed)
                np.random.seed(seed)
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)
                if hasattr(torch, 'xpu') and torch.xpu.is_available():
                    torch.xpu.manual_seed_all(seed)
                solved, exp, cost, actions, seconds, stats = dispatch(
                    method, boards[map_id - 1], loaded[0], loaded[1:], device, args.boxes, timeout, cap)
                actions = list(map(int, actions))
                verified = bool(solved and replay_plan(boards[map_id - 1], actions))
                if solved and (not verified or cost != len(actions)):
                    raise ValueError('Invalid returned solution')
                row = {'map_id': map_id, 'method': method, 'seed': seed, 'solved': bool(solved),
                       'verified': verified, 'expansions': int(exp), 'cost': float(cost) if solved else None,
                       'actions': actions, 'time_sec': float(seconds), 'evidence': 'new_run',
                       'run_fingerprint': fingerprint(meta), **stats}
                f.write(json.dumps(row, allow_nan=False) + '\n')
                f.flush()
                os.fsync(f.fileno())
                print(f'map={map_id} method={method} solved={solved} expansions={exp} time={seconds:.3f}s', flush=True)
    finally:
        lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boxes', type=int, choices=[3, 5, 7], required=True)
    parser.add_argument('--methods', nargs='+', choices=list(METHODS))
    parser.add_argument('--profile', choices=['uniform', 'historical'], default='uniform')
    parser.add_argument('--device', default='auto')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--start-map', type=int, default=1)
    parser.add_argument('--end-map', type=int)
    parser.add_argument('--wall-hours', type=float, default=11.75)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke-test', action='store_true')
    args = parser.parse_args()
    if args.wall_hours <= 0:
        parser.error('wall-hours must be positive')
    run(args)
