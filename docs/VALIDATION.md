# Validation checks

- Project tests cover the registry, supported settings, budgets, asset hashes, archived plan replay, percentile offset invariance, incomplete-run detection, failed-attempt timing, and rejection of invalid plans.
- All ten selected methods solve the one-push smoke board using the actual six copied checkpoints.
- IID/OOD baseline search, single-member search, MC heuristic, MC A* and fixed-half hybrid retain identical syntax trees to their inherited implementations.
- Pruned ensemble evaluation matches inherited selected configurations on actual checkpoint predictions across sequential candidate batches.
- Maximum absolute differences: {"conf20": 0.0, "conf50": 0.0, "risk1": 0.0}.
- Copied datasets and checkpoints retain SHA256 identities; 553 archived seven-box solved plans replay independently, including partial map-95 attempts. The comparison cohort is maps 1–94; three completed map-95 attempts are separate. Archived records agree with all previously reported live-log solve flags and expansion counts.

Run `python tools/sanity_check.py --device cpu` for asset verification, saved five-map replay, and actual-checkpoint smoke execution through all ten methods. See [REPRODUCING.md](REPRODUCING.md) for the five-map evaluation workflow.

## Reproduction workflow verification

- All nine automated checks pass.
- The CPU sanity command verifies 11 asset checksums, 100 frozen seven-box boards, and 35 saved plans from maps 1–5.
- All ten methods solve the one-push check and the first real seven-box map; every returned plan replays independently.
- Run reports detect incomplete attempt grids and reject invalid plans. Repeating the completed real-map command adds no duplicate records.
- The extracted cloud bundle passes the same sanity command.
