import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.methods import METHODS
from src.protocol import fingerprint
from tools.report_run import summarize


class RunReportTests(unittest.TestCase):
    def fixture(self, path, missing=False):
        meta = {'kind': 'smoke_validation', 'boxes': 7, 'hardware': 'CPU',
                'methods': list(METHODS), 'requested_maps': [1]}
        (path / 'metadata.json').write_text(json.dumps(meta), encoding='utf-8')
        rows = [{'map_id': 1, 'method': method, 'solved': True, 'verified': True,
                 'expansions': 2, 'cost': 1, 'actions': [4], 'time_sec': 0.1,
                 'wall_time_sec': 0.2, 'run_fingerprint': fingerprint(meta)} for method in METHODS]
        if missing:
            rows.pop()
        return rows

    def write(self, path, rows):
        (path / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')

    def test_incomplete_grid_is_not_reported_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            self.write(path, self.fixture(path, missing=True))
            with self.assertRaisesRegex(ValueError, 'Incomplete grid'):
                summarize(path, expected_maps=1, require_all_methods=True)
            self.assertFalse(json.loads((path / 'summary.json').read_text())['complete'])

    def test_failures_count_in_runtime_and_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            rows = self.fixture(path)
            rows[0].update(solved=False, verified=False, cost=None, actions=[], time_sec=10, wall_time_sec=10.2)
            self.write(path, rows)
            result = summarize(path, expected_maps=1, require_all_methods=True)
            self.assertTrue(result['complete'])
            self.assertEqual(result['tables'][0]['solved'], 0)
            self.assertEqual(result['tables'][0]['mean_search_time_sec'], 10)
            self.assertIsNone(result['tables'][0]['mean_expansions'])

    def test_invalid_solution_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            rows = self.fixture(path)
            rows[0]['actions'] = [5]
            self.write(path, rows)
            with self.assertRaisesRegex(ValueError, 'Solution replay failed'):
                summarize(path, expected_maps=1)


if __name__ == '__main__':
    unittest.main()
