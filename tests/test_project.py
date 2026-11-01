import inspect
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import sha256, replay_plan, smoke_board, read_boards
from src.ensemble_search import DeepEnsembleHeuristic, run_ensemble_astar
from src.sokoban_env import SokobanEnv
from benchmarks.run_benchmark import budget


class ProjectTests(unittest.TestCase):
    def test_exact_method_registry(self):
        expected = {'classical_astar', 'paper_astar', 'paper_gbfs', 'fixed_hybrid_astar',
                    'paper_mc_astar', 'single_astar', 'single_mc_astar',
                    'ensemble_conf_020', 'ensemble_conf_050', 'ensemble_risk'}
        self.assertEqual(set(METHODS), expected)
        self.assertNotIn('fixed_lambda', inspect.signature(run_ensemble_astar).parameters)
        self.assertNotIn('fixed_lambda', inspect.signature(DeepEnsembleHeuristic.evaluate_batch).parameters)

    def test_restricted_constructor_settings(self):
        state = smoke_board()
        targets = SokobanEnv.get_box_targets(state)
        goal = SokobanEnv.get_goal_state(state, targets)
        with self.assertRaises(ValueError):
            DeepEnsembleHeuristic([None] * 5, goal, targets, torch.device('cpu'), lambda_min=1.0)
        with self.assertRaises(ValueError):
            DeepEnsembleHeuristic([None] * 5, goal, targets, torch.device('cpu'), search_mode='risk_averse', kappa=0)

    def test_uniform_and_historical_budgets(self):
        for method in METHODS:
            self.assertEqual(budget(7, method, 'uniform'), (360, 1_000_000))
        self.assertEqual(budget(3, 'paper_astar', 'historical'), (600, 100_000))
        self.assertEqual(budget(5, 'paper_astar', 'historical'), (600, 15_000))
        self.assertEqual(budget(5, 'classical_astar', 'historical'), (600, 150_000))

    def test_copied_asset_hashes(self):
        hashes = json.loads((ROOT / 'data/assets_sha256.json').read_text())
        for relative, expected in hashes.items():
            self.assertEqual(sha256(ROOT / relative), expected, relative)

    def test_retained_evidence_and_replay(self):
        boards = read_boards(ROOT / 'data/sokoban_7box_original_test.txt')
        count = 0
        for folder in (ROOT / 'results').iterdir():
            if not folder.is_dir() or not (folder / 'records.jsonl').exists():
                continue
            rows = [json.loads(line) for line in (folder / 'records.jsonl').read_text().splitlines()]
            self.assertEqual(len({(r['map_id'], r['method']) for r in rows}), len(rows))
            self.assertTrue(all(r['method'] in METHODS for r in rows))
            for row in rows:
                if row.get('evidence') == 'archived_plan' and row['solved']:
                    self.assertTrue(replay_plan(boards[row['map_id'] - 1], row['actions']))
            count += len(rows)
        self.assertEqual(count, 3061)

    def test_percentile_uncertainty_is_offset_invariant(self):
        class Model(torch.nn.Module):
            def __init__(self, member, offset):
                super().__init__()
                self.offset = offset
                self.register_buffer('weights', torch.arange(100, dtype=torch.float32).reshape(10, 10).roll(member, 0))
            def forward(self, state, goal):
                return (state[:, 3] * self.weights).sum(dim=(1, 2)) + self.offset
        initial = smoke_board()
        targets = SokobanEnv.get_box_targets(initial)
        goal = SokobanEnv.get_goal_state(initial, targets)
        states = []
        for r in range(1, 8):
            s = initial.copy()
            s[4, 2] = 1
            s[r, 1] = 3
            states.append(s)
        for mode in ['convex', 'risk_averse']:
            a = DeepEnsembleHeuristic([Model(i, 0) for i in range(5)], goal, targets, torch.device('cpu'), search_mode=mode)
            b = DeepEnsembleHeuristic([Model(i, 1000 * i - 2000) for i in range(5)], goal, targets, torch.device('cpu'), search_mode=mode)
            x, y = a.evaluate_batch(states), b.evaluate_batch(states)
            np.testing.assert_allclose([e.h_blend for e in x], [e.h_blend for e in y])
            np.testing.assert_allclose([e.variance for e in x], [e.variance for e in y])


if __name__ == '__main__':
    unittest.main()
