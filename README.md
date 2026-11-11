# Risk-aware A* search for Sokoban

Confidence-aware and risk-aware neural heuristic search for **10×10 Sokoban**.
The project evaluates models trained on three-box puzzles on **3-box IID,
5-box OOD, and 7-box OOD** tasks. Trained checkpoints, fixed test sets, results,
and solution replays are included. **No training or puzzle generation is needed
to run the examples.**

[Results](RESULTS.md) · [Reproduce the experiments](docs/REPRODUCING.md) ·
[Method formulas](docs/METHODS.md) · [Gallery](sokoban_visuals_v2/README.md)

## Start here

Clone the repository and install the evaluation dependencies:

```bash
git clone https://github.com/harshit-iitr/Risk_averse_A_search.git
cd Risk_averse_A_search
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
```

Use a PyTorch build that supports your accelerator to run on NVIDIA CUDA or
Intel XPU. CPU evaluation also works. `--device auto` selects CUDA, then XPU,
then CPU; specify `--device cpu`, `--device cuda:0`, or `--device xpu` explicitly
when comparing runs.

## Fast sanity check

```bash
python tools/sanity_check.py --device cpu
```

This checks the included asset hashes and frozen seven-box boards, replays saved
successful solutions from the first **five seven-box maps**, and runs **all ten
methods** with the actual checkpoints on a one-push puzzle. It prints a final
`PASS` only when every check succeeds. The one-push execution verifies the setup;
the next command performs the real seven-box experiment.

## Reproduce five seven-box maps with every method

```bash
python benchmarks/run_benchmark.py --boxes 7 --start-map 1 --end-map 5 --device auto --threads 2 --output output/seven_box_5maps
python tools/report_run.py output/seven_box_5maps --expected-maps 5 --require-all-methods
```

Omitting `--methods` selects **all ten supported methods**. This gives 50 attempts,
with 360 seconds and 1,000,000 expansions available per attempt. Allow up to
**five hours of search time**, plus setup, for this real benchmark; use the fast
sanity check first. Actual runtime depends on the device and puzzle outcomes.

The output folder contains:

| File | Contents |
|---|---|
| `metadata.json` | Device, software versions, seeds, budgets, source and asset hashes |
| `records.jsonl` | One record per attempt, including actions and timings |
| `report.md` | Readable results table for this run |
| `summary.csv` / `summary.json` | Results for further analysis |

Every returned solution is replayed independently. Repeat the benchmark command
with the same output folder to resume missing attempts. Run the report command
again after completion. See [the reproduction guide](docs/REPRODUCING.md) for
selected methods, full cohorts, and cloud packaging.

## Included methods

| Method | Command-line ID |
|---|---|
| Classical A* | `classical_astar` |
| Paper Learned A* (2023) | `paper_astar` |
| Paper Learned GBFS | `paper_gbfs` |
| Fixed 50/50 Hybrid A* | `fixed_hybrid_astar` |
| MC Confidence-Aware A* — paper model | `paper_mc_astar` |
| Single Scratch Model #0 A* | `single_astar` |
| MC-Dropout on Scratch Model #0 | `single_mc_astar` |
| Confidence-Aware Ensemble A* | `ensemble_conf_020` |
| Calibrated Confidence-Aware Ensemble A* | `ensemble_conf_050` |
| Risk-Averse Ensemble A* | `ensemble_risk` |

The confidence settings refer to learned-weight floors **0.20 and 0.50**.
Both use heuristic scale **C = 50**. Risk-aware search uses **κ = 1**.
[Method details and the complete parameter table](docs/METHODS.md).

## Results and visuals

[RESULTS.md](RESULTS.md) contains the three domain tables, elapsed timings, and
paired comparisons. The seven-box comparison covers **94 fixed maps**; GBFS has
a separately labelled five-map pilot, and completed map-95 attempts are listed
separately. The gallery contains plots and diagnostic Sokoban replays with their
cohort labels. Historical figures use an 82-map snapshot.

For example, on the **70 seven-box puzzles solved by both methods**, the
risk-aware pipeline averages **2,592.9 expansions** versus **19,496.9** for
Paper Learned A*: a **7.52× ratio of mean expansions**. In the 94-map cohort,
the methods solve 74 and 70 puzzles, respectively.

## Repository map

| Location | Purpose |
|---|---|
| `src/` | Model, Sokoban environment, heuristics, and search implementations |
| `benchmarks/` | Seeded evaluation runner |
| `checkpoints/ensemble/` | Five trained members |
| `finalSok3_pytorch.pt` | Included paper-model checkpoint |
| `data/` | Training and frozen evaluation puzzles, provenance, and checksums |
| `results/` | Recorded experiments and machine-readable summaries |
| `tools/` | Sanity check, run reports, cloud packaging, and optional training |
| `tests/` | Automated project checks |
| `sokoban_visuals_v2/` | HTML gallery, figures, and replay assets |

For development checks:

```bash
python -m unittest discover -s tests -v
```

## References and attribution

The Paper Learned methods follow the project implementation based on
[Chrestien et al., *Optimize Planning Heuristics to Rank, not to Estimate
Cost-to-Goal*, NeurIPS 2023](https://arxiv.org/abs/2310.19463).
The upstream license is retained in [licenses/UPSTREAM_CC0.txt](licenses/UPSTREAM_CC0.txt).
Dataset and checkpoint identities are recorded in `data/assets_sha256.json`.
