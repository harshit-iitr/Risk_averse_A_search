# Project workflow

Support the ten method IDs in `src/methods.py`. Preserve checkpoints, frozen
puzzles and per-map results. Keep output from new runs under `output/`.

Start with `python tools/sanity_check.py --device cpu`. For five real seven-box
maps across all methods, follow README.md and docs/REPRODUCING.md. Generate local
run reports with tools/report_run.py; archived tables use tools/build_report.py.

Compute ensemble disagreement in each member's percentile space. Keep the
recorded confidence and risk priority formulas. Keep all credentials out of Git.

Seven-box archived results cover 94 common maps, plus a separate five-map GBFS
pilot and partial map-95 records. Keep cohort, timing and device labels accurate.
