# Reproducing the Sokoban experiments

Run commands from the repository root after installing `requirements.txt`.
The checkpoints and all evaluation maps are included in a normal Git clone.
Evaluation requires PyTorch, NumPy, and SciPy. Generation dependencies in
`requirements-generation.txt` are only needed when generating new puzzles.

## 1. Verify the installation

```bash
python tools/sanity_check.py --device cpu
```

This verifies asset checksums, frozen seven-box board structure and uniqueness,
saved solutions on maps 1–5, and actual model inference and search through all
ten methods. Each method must solve and replay a one-push validation puzzle.
Outputs are saved under a newly created `output/sanity_*` folder.

Use `--device cuda:0`, `--device xpu`, or `--device auto` to test an accelerator.
The script exits with a nonzero status when a check fails.

## 2. Run the first five seven-box puzzles

```bash
python benchmarks/run_benchmark.py --boxes 7 --start-map 1 --end-map 5 --device auto --threads 2 --seed 42 --output output/seven_box_5maps
python tools/report_run.py output/seven_box_5maps --expected-maps 5 --require-all-methods
```

All ten methods run by default: 5 maps × 10 methods = **50 attempts**. Every
attempt receives 360 seconds and a 1,000,000-expansion ceiling. The full timeout
allowance is five hours, plus dispatch and setup. A timeout is recorded as a
completed unsuccessful attempt; it does not prevent the suite from continuing.

The report command validates recorded fingerprints and returned plans, writes
Markdown/CSV/JSON tables, and verifies the requested map/method coverage. It
exits nonzero if the 50-attempt grid is incomplete. An experiment can contain
unsolved puzzles and still be a complete, valid evaluation.

The archived seven-box results include eight full-cohort A* methods and a
five-map GBFS pilot. Fixed 50/50 is also supported by the reproduction runner;
new outputs are saved separately from the archived experiments.

## 3. Select a smaller comparison

```bash
python benchmarks/run_benchmark.py --boxes 7 --start-map 1 --end-map 5 --methods paper_astar paper_mc_astar ensemble_conf_050 ensemble_risk --device auto --threads 2 --output output/seven_box_selected
python tools/report_run.py output/seven_box_selected --expected-maps 5
```

The report expects the four selected methods on all five maps. Drop
`--expected-maps` to inspect partial progress without requiring a complete grid.

## 4. Resume and inspect progress

Every attempt is saved to `records.jsonl` before the next starts. Repeat the
same benchmark command and output folder to continue missing attempts. The
runner checks that the code, assets, device, software, seed, and profile match.

```bash
python tools/report_run.py output/seven_box_5maps
```

This produces an interim report from the attempts already saved. The progress
log prints each method before execution and its outcome afterwards. The default
session allowance is 11.75 hours; use `--wall-hours` to set a shorter session.
The runner reserves the full next-attempt timeout before starting it.

An active output directory uses `.run.lock` to prevent concurrent writers. After
a forced termination, first confirm no process is writing there before removing
that stale lock. Use a new output folder for a different configuration.

## 5. Run complete cohorts

```bash
python benchmarks/run_benchmark.py --boxes 3 --end-map 200 --device auto --threads 2 --output output/three_box
python benchmarks/run_benchmark.py --boxes 5 --end-map 100 --device auto --threads 2 --output output/five_box
python benchmarks/run_benchmark.py --boxes 7 --end-map 94 --device auto --threads 2 --output output/seven_box
```

The default `uniform` profile gives all methods the same 360-second /
1,000,000-expansion settings. The runner also provides `--profile historical`
for the recorded three- and five-box protocol families. Per-method settings for
each new run appear in `metadata.json`. Keep device, seed and profile fixed for
a comparison. GPU execution and installed numerical libraries can affect
elapsed times and search ordering; use the saved records for the run you report.

## 6. Read the outputs

`report.md` lists solve counts, expansions on solved maps, mean solution cost,
mean search time, and mean elapsed time including dispatch. Time averages include
failed attempts. Metadata records Python/PyTorch/NumPy versions, the device,
thread count, checkpoint hashes, source hashes, and the frozen dataset hash.
`requirements_resolved.txt` captures the installed Python package versions.

The project-level [RESULTS.md](../RESULTS.md) is built from archived `results/`
folders. To regenerate it, run:

```bash
python tools/build_report.py
```

For new local outputs, use `tools/report_run.py`; this keeps demonstration runs
separate from archived result tables.

## 7. Run in a cloud environment

```bash
python tools/package_cloud.py --output output/sokoban_reproduction.zip
```

Extract the archive into your working directory, install `requirements.txt`,
and use the same five-map command. The archive includes execution code,
checkpoints, fixed test data, documentation, and the upstream license. No Kaggle
key is needed inside the bundle. Prefer a `/kaggle/working/...` output path in
Kaggle so completed records can be downloaded.

## Automated checks

```bash
python -m unittest discover -s tests -v
```

The suite checks the method registry, supported settings, asset hashes, retained
plan replay, percentile offset invariance, and per-profile budgets. The sanity
command additionally exercises actual checkpoint inference through all methods.
