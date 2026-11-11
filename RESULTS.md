# Sokoban experiment results

[Project overview](README.md) · [Reproduce a run](docs/REPRODUCING.md) · [Methods](docs/METHODS.md)

Tables report the recorded cohorts, devices and evaluation settings. Expansion
and solution-cost statistics use solved puzzles. Paired comparisons use puzzles
solved by both methods. Mean elapsed times include every attempt, including
failures: **S** denotes search-only timing and **D** includes dispatch setup.
One-time model loading and puzzle generation are outside these timings.

The seven-box comparison covers **94 fixed maps**, with independently replayed
successful plans. GBFS has a separate **five-map pilot**. Completed attempts from
partial map 95 appear below the common-cohort table. Raw records, checkpoint
identities and experiment metadata are retained in `results/` and `data/`.

## 3-box Sokoban — IID

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost | Mean elapsed wall time (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Classical A* | XPU | 600 / 100,000 | 195/200 (97.5%) | 11,133.3 | 3,370.0 | 36,299.8 | 26.0 | 0.28 S |
| Paper Learned A* (2023) | XPU | 600 / 100,000 | 200/200 (100.0%) | 1,262.9 | 224.5 | 3,694.1 | 26.6 | 4.52 S |
| Paper Learned GBFS | XPU | 600 / 100,000 | 200/200 (100.0%) | 944.4 | 43.0 | 1,689.8 | 31.3 | 2.92 S |
| Fixed 50/50 Hybrid A* | XPU | 600 / 100,000 | 200/200 (100.0%) | 762.2 | 155.5 | 1,719.3 | 29.0 | 3.66 S |
| MC Confidence-Aware A* — paper model | XPU | 600 / 100,000 | 200/200 (100.0%) | 596.0 | 92.0 | 1,393.5 | 28.4 | 3.04 S |
| Single Scratch Model #0 A* | XPU | 360 / 1,000,000 | 200/200 (100.0%) | 1,222.3 | 121.0 | 3,446.8 | 27.1 | 3.86 S |
| Confidence-Aware Ensemble A* (conf_20) | XPU | 360 / 1,000,000 | 200/200 (100.0%) | 377.9 | 90.0 | 708.1 | 29.4 | 5.93 S |

## 5-box Sokoban — OOD

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost | Mean elapsed wall time (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Classical A* | XPU | 600 / 150,000 | 56/100 (56.0%) | 41,546.2 | 26,794.0 | 104,652.0 | 31.7 | 2.51 S |
| Paper Learned A* (2023) | XPU | 600 / 15,000 | 71/100 (71.0%) | 2,833.8 | 1,384.0 | 8,354.0 | 33.5 | 25.27 S |
| Paper Learned GBFS | XPU | 600 / 15,000 | 70/100 (70.0%) | 2,516.1 | 346.0 | 8,529.8 | 45.9 | 22.95 S |
| MC Confidence-Aware A* — paper model | XPU | 600 / 15,000 | 90/100 (90.0%) | 1,970.5 | 567.5 | 6,921.5 | 38.3 | 17.23 S |
| Single Scratch Model #0 A* | XPU | 360 / 1,000,000 | 93/100 (93.0%) | 8,740.4 | 1,436.0 | 25,827.2 | 37.5 | 51.85 S |
| MC-Dropout on Scratch Model #0 | XPU | 360 / 1,000,000 | 77/100 (77.0%) | 7,906.9 | 3,042.0 | 20,360.2 | 36.4 | 113.53 S |
| Confidence-Aware Ensemble A* (conf_20) | XPU | 360 / 1,000,000 | 95/100 (95.0%) | 1,614.9 | 549.0 | 4,601.8 | 41.0 | 43.62 S |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | RTX 3050 | 360 / 1,000,000 | 92/100 (92.0%) | 1,391.6 | 501.5 | 4,065.6 | 40.5 | 67.46 S |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | XPU | 360 / 1,000,000 | 94/100 (94.0%) | 1,553.5 | 513.0 | 4,697.7 | 40.8 | 44.73 S |
| Risk-Averse Ensemble A* (kappa=1) | RTX 3050 | 360 / 1,000,000 | 94/100 (94.0%) | 1,354.8 | 393.0 | 4,122.2 | 41.6 | 59.84 S |

## 7-box Sokoban — OOD

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost | Mean elapsed wall time (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Classical A* | Tesla T4 | 360 / 1,000,000 | 47/94 (50.0%) | 296,693.8 | 143,415.0 | 821,621.4 | 36.7 | 41.70 D |
| Paper Learned A* (2023) | Tesla T4 | 360 / 1,000,000 | 70/94 (74.5%) | 19,496.9 | 5,769.5 | 62,287.1 | 39.7 | 127.67 D |
| Paper Learned GBFS | Tesla T4 | 360 / 1,000,000 | 4/5 (80.0%) | 40,236.8 | 1,606.5 | 111,265.2 | 46.0 | 140.89 D |
| MC Confidence-Aware A* — paper model | Tesla T4 | 360 / 1,000,000 | 74/94 (78.7%) | 9,225.0 | 1,340.5 | 27,127.3 | 43.7 | 100.37 D |
| Single Scratch Model #0 A* | Tesla T4 | 360 / 1,000,000 | 76/94 (80.9%) | 13,638.5 | 1,936.5 | 44,062.0 | 42.6 | 97.12 D |
| MC-Dropout on Scratch Model #0 | Tesla T4 | 360 / 1,000,000 | 61/94 (64.9%) | 14,249.0 | 6,997.0 | 35,963.0 | 40.8 | 157.25 D |
| Confidence-Aware Ensemble A* (conf_20) | Tesla T4 | 360 / 1,000,000 | 73/94 (77.7%) | 3,349.6 | 902.0 | 11,752.8 | 44.8 | 112.73 D |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | Tesla T4 | 360 / 1,000,000 | 72/94 (76.6%) | 3,412.2 | 826.5 | 11,118.0 | 44.9 | 116.97 D |
| Risk-Averse Ensemble A* (kappa=1) | Tesla T4 | 360 / 1,000,000 | 74/94 (78.7%) | 3,112.9 | 735.5 | 11,788.3 | 45.7 | 107.25 D |

## Partial map 95 — excluded from the 94-map comparison

| Method | Solved | Expansions | Search time (s) | Cost | Wall time (s) |
|---|---|---:|---:|---:|---:|
| Classical A* | True | 863,132 | 46.04 | 66 | 46.76 |
| Paper Learned A* (2023) | True | 117,898 | 262.06 | 66 | 262.20 |
| MC Confidence-Aware A* — paper model | False | 113,862 | 360.00 | — | 360.27 |

Other methods did not finish map 95; missing attempts are not failures. Fixed 50/50 Hybrid A* has no seven-box results.

## Paired comparisons within recorded runs

- `iid_3box_legacy`: MC Confidence-Aware A* — paper model vs Paper Learned A* (2023): N=200; 164W/1T/35L; mean expansion reduction 52.81% (negative means more expansions).
- `ood_5box_legacy`: MC Confidence-Aware A* — paper model vs Paper Learned A* (2023): N=70; 62W/0T/8L; mean expansion reduction 64.12% (negative means more expansions).
- `ood_5box_risk`: Risk-Averse Ensemble A* (kappa=1) vs Calibrated Confidence-Aware Ensemble A* (conf_50): N=92; 65W/1T/26L; mean expansion reduction 13.56% (negative means more expansions).
- `ood_7box_snapshot94`: MC Confidence-Aware A* — paper model vs Paper Learned A* (2023): N=70; 62W/0T/8L; mean expansion reduction 63.20% (negative means more expansions).
- `ood_7box_snapshot94`: MC-Dropout on Scratch Model #0 vs Single Scratch Model #0 A*: N=61; 4W/0T/57L; mean expansion reduction -258.48% (negative means more expansions).
- `ood_7box_snapshot94`: Risk-Averse Ensemble A* (kappa=1) vs Confidence-Aware Ensemble A* (conf_20): N=73; 52W/0T/21L; mean expansion reduction 14.60% (negative means more expansions).
- `ood_7box_snapshot94`: Risk-Averse Ensemble A* (kappa=1) vs Calibrated Confidence-Aware Ensemble A* (conf_50): N=72; 54W/1T/17L; mean expansion reduction 27.56% (negative means more expansions).
