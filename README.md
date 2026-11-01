# Risk-averse heuristic search for Sokoban

A focused college research project evaluating confidence-aware and risk-aware
neural heuristic search. Models trained on three-box Sokoban are evaluated on
three-box IID, five-box OOD and seven-box OOD puzzles on 10x10 grids.

## Supported experiments

1. Classical A*.
2. Paper Learned A*, using the original repository's unchanged checkpoint.
3. Paper Learned GBFS.
4. Fixed 50/50 Hybrid A*.
5. MC Confidence-Aware A* — paper model.
6. Single Scratch Model #0 A*.
7. MC-Dropout on Scratch Model #0.
8. Confidence-Aware Ensemble A* (`conf_20`).
9. Calibrated Confidence-Aware Ensemble A* (`conf_50`).
10. Risk-Averse Ensemble A* (`kappa=1`).

The registry in `src/methods.py` is the supported method inventory. No absent
domain/method combination is treated as an executed experiment.

## Results and evidence

Read [RESULTS.md](RESULTS.md) for the three tables and paired comparisons.
Historical three-box and five-box results retain their original hardware and
budgets. Seven-box reporting uses **82 of 100 fixed maps**, 360 seconds and
1,000,000 expansions per method. Its first 45 maps have archived raw records;
maps 46–82 have completed live-log observations with plans/costs still pending
raw export. Paper Learned GBFS has only five seven-box records. These are
separate evaluation cohorts, explicitly labelled in the report.

The six existing checkpoints and datasets are copied byte-for-byte. Asset hashes
are in `data/assets_sha256.json`. The historical name “Paper Learned” does not
establish a verified reproduction of the published paper. “Scratch Model #0” is
a retained experiment label; the provided training utility supports both fresh
initialization and warm starts, so the name alone is not training provenance.

## Methods

Let `p_m(s)` be each member's own online percentile, with mean `mu_p`, variance
`v_p` and standard deviation `sigma_p`. This makes disagreement invariant to
constant cross-model offsets.

- MC confidence gate: `lambda = 0.2 + 0.8 * max(0, 1 - 4*v_p)`.
- Ensemble confidence gate: `lambda = lambda_min + (1-lambda_min)*max(0, 1-2.5*sigma_p)`, with `lambda_min=0.2` or `0.5`.
- Confidence priority: `f = g + 50*(lambda*mu_p + (1-lambda)*p_classical)`.
- Risk priority: `f = g + 50*min(1, mu_p + sigma_p)`.
- Fixed hybrid: the MC-based percentile blend with `lambda=0.5`.

All MC configurations use five samples with dropout 0.10. The ensemble
configurations use five trained members. The classical heuristic uses minimum
Manhattan bipartite matching. The retained experiments do not use symbolic
deadlock pruning. Original loop behavior, tie breaking and stopping counters are
preserved; timeout/expansion checks can slightly overrun their nominal boundary.

## Run

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python benchmarks/run_benchmark.py --boxes 7 --smoke-test --device cpu --output output/smoke
python benchmarks/run_benchmark.py --boxes 7 --methods paper_astar paper_mc_astar ensemble_conf_020 ensemble_conf_050 ensemble_risk --start-map 1 --end-map 100 --device cuda:0 --output output/seven_box
```

The default `uniform` profile gives every selected method 360 seconds and
1,000,000 expansions. `--profile historical` retains the recorded 3/5-box budget
families; it is not a claim of identical wall-clock or stochastic outcomes.
Three-box baseline search keeps its original goal-score behavior separately
from the five/seven-box baseline. Each invocation has an 11.75-hour wall allowance
by default and saves every attempt. Repeat the same command/output to resume;
code, data, checkpoints, device, seed and settings must match. Separate jobs need
separate output directories. A one-push smoke run is validation, not benchmark data.

```bash
python tools/build_report.py
python tools/package_cloud.py
```

The cloud zip contains an explicit allowlist of code, checkpoints, test data and
upstream license. It contains no credentials. Extract it into a Kaggle GPU
session and run the benchmark command above with a `/kaggle/working/...` output
directory. Frozen seven-box data is included: regeneration is unnecessary.

Optional training code is retained in `tools/train_deep_ensemble.py`; no new
training was done for this migration. Generator dependencies are separated in
`requirements-generation.txt`. Never replace the frozen evaluation set.

## Limitations

MC helps the legacy checkpoint but harms trained M0 in the recorded comparisons.
Dropout sensitivity and gating interactions are hypotheses, not established
causes. “Calibrated” identifies the gate setting, not statistical error calibration.
Uncertainty has not been established as a predictor of distance error. Learned
heuristics do not guarantee optimal solutions. Upstream CC0 text is preserved
in `licenses/UPSTREAM_CC0.txt`; no new rights over checkpoints are asserted.


## Gallery and figures

Browse the [visual gallery and captions](sokoban_visuals_v2/README.md) for plots, SVG exports and animated Sokoban replays. Open [gallery.html](sokoban_visuals_v2/gallery.html) locally for the complete HTML layout. The Map 76 animations are separately captured diagnostic trajectories, with benchmark numbers and provenance clearly labelled.
