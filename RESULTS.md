# Sokoban experiment results

Only the ten methods in `src/methods.py` are supported. Tables retain recorded
hardware and budgets; historical groups are not one controlled cross-device
comparison. Expansions and costs use solved maps. Compare expansions on mutually
solved maps for a paired claim. Unperformed combinations are not invented.

The seven-box comparison uses **94/100 fixed maps**, with archived raw records
and independently replayed successful plans throughout. The completed Kaggle
session stopped partway through map 95; its three completed attempts are listed
separately and excluded from the common-cohort table and paired comparisons.
Paper Learned GBFS covers only maps 1–5, not the 94-map cohort. Method names
retain historical terminology; checkpoint identity as a published paper model
is not verified.

## 3-box Sokoban — IID

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost |
|---|---|---|---:|---:|---:|---:|---:|
| Classical A* | XPU | 600 / 100,000 | 195/200 (97.5%) | 11,133.3 | 3,370.0 | 36,299.8 | 26.0 |
| Paper Learned A* (legacy checkpoint) | XPU | 600 / 100,000 | 200/200 (100.0%) | 1,262.9 | 224.5 | 3,694.1 | 26.6 |
| Paper Learned GBFS | XPU | 600 / 100,000 | 200/200 (100.0%) | 944.4 | 43.0 | 1,689.8 | 31.3 |
| Fixed 50/50 Hybrid A* | XPU | 600 / 100,000 | 200/200 (100.0%) | 762.2 | 155.5 | 1,719.3 | 29.0 |
| MC Confidence-Aware A* — paper model | XPU | 600 / 100,000 | 200/200 (100.0%) | 596.0 | 92.0 | 1,393.5 | 28.4 |
| Single Scratch Model #0 A* | XPU | 360 / 1,000,000 | 200/200 (100.0%) | 1,222.3 | 121.0 | 3,446.8 | 27.1 |
| Confidence-Aware Ensemble A* (conf_20) | XPU | 360 / 1,000,000 | 200/200 (100.0%) | 377.9 | 90.0 | 708.1 | 29.4 |

## 5-box Sokoban — OOD

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost |
|---|---|---|---:|---:|---:|---:|---:|
| Classical A* | XPU | 600 / 150,000 | 56/100 (56.0%) | 41,546.2 | 26,794.0 | 104,652.0 | 31.7 |
| Paper Learned A* (legacy checkpoint) | XPU | 600 / 15,000 | 71/100 (71.0%) | 2,833.8 | 1,384.0 | 8,354.0 | 33.5 |
| Paper Learned GBFS | XPU | 600 / 15,000 | 70/100 (70.0%) | 2,516.1 | 346.0 | 8,529.8 | 45.9 |
| MC Confidence-Aware A* — paper model | XPU | 600 / 15,000 | 90/100 (90.0%) | 1,970.5 | 567.5 | 6,921.5 | 38.3 |
| Single Scratch Model #0 A* | XPU | 360 / 1,000,000 | 93/100 (93.0%) | 8,740.4 | 1,436.0 | 25,827.2 | 37.5 |
| MC-Dropout on Scratch Model #0 | XPU | 360 / 1,000,000 | 77/100 (77.0%) | 7,906.9 | 3,042.0 | 20,360.2 | 36.4 |
| Confidence-Aware Ensemble A* (conf_20) | XPU | 360 / 1,000,000 | 95/100 (95.0%) | 1,614.9 | 549.0 | 4,601.8 | 41.0 |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | RTX 3050 | 360 / 1,000,000 | 92/100 (92.0%) | 1,391.6 | 501.5 | 4,065.6 | 40.5 |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | XPU | 360 / 1,000,000 | 94/100 (94.0%) | 1,553.5 | 513.0 | 4,697.7 | 40.8 |
| Risk-Averse Ensemble A* (kappa=1) | RTX 3050 | 360 / 1,000,000 | 94/100 (94.0%) | 1,354.8 | 393.0 | 4,122.2 | 41.6 |

## 7-box Sokoban — OOD

| Method | Hardware | Budget (s / exp.) | Solved | Mean exp. | Median exp. | P90 exp. | Mean cost |
|---|---|---|---:|---:|---:|---:|---:|
| Classical A* | Tesla T4 | 360 / 1,000,000 | 47/94 (50.0%) | 296,693.8 | 143,415.0 | 821,621.4 | 36.7 |
| Paper Learned A* (legacy checkpoint) | Tesla T4 | 360 / 1,000,000 | 70/94 (74.5%) | 19,496.9 | 5,769.5 | 62,287.1 | 39.7 |
| Paper Learned GBFS | Tesla T4 | 360 / 1,000,000 | 4/5 (80.0%) | 40,236.8 | 1,606.5 | 111,265.2 | 46.0 |
| MC Confidence-Aware A* — paper model | Tesla T4 | 360 / 1,000,000 | 74/94 (78.7%) | 9,225.0 | 1,340.5 | 27,127.3 | 43.7 |
| Single Scratch Model #0 A* | Tesla T4 | 360 / 1,000,000 | 76/94 (80.9%) | 13,638.5 | 1,936.5 | 44,062.0 | 42.6 |
| MC-Dropout on Scratch Model #0 | Tesla T4 | 360 / 1,000,000 | 61/94 (64.9%) | 14,249.0 | 6,997.0 | 35,963.0 | 40.8 |
| Confidence-Aware Ensemble A* (conf_20) | Tesla T4 | 360 / 1,000,000 | 73/94 (77.7%) | 3,349.6 | 902.0 | 11,752.8 | 44.8 |
| Calibrated Confidence-Aware Ensemble A* (conf_50) | Tesla T4 | 360 / 1,000,000 | 72/94 (76.6%) | 3,412.2 | 826.5 | 11,118.0 | 44.9 |
| Risk-Averse Ensemble A* (kappa=1) | Tesla T4 | 360 / 1,000,000 | 74/94 (78.7%) | 3,112.9 | 735.5 | 11,788.3 | 45.7 |

## Partial map 95 — excluded from the 94-map comparison

| Method | Solved | Expansions | Search time (s) | Cost |
|---|---|---:|---:|---:|
| Classical A* | True | 863,132 | 46.04 | 66 |
| Paper Learned A* (legacy checkpoint) | True | 117,898 | 262.06 | 66 |
| MC Confidence-Aware A* — paper model | False | 113,862 | 360.00 | — |

Other methods did not finish map 95; missing attempts are not failures. Fixed 50/50 Hybrid A* has no seven-box results.

## Paired comparisons within recorded runs

- `iid_3box_legacy`: MC Confidence-Aware A* — paper model vs Paper Learned A* (legacy checkpoint): N=200; 164W/1T/35L; mean expansion reduction 52.81% (negative means more expansions).
- `ood_5box_legacy`: MC Confidence-Aware A* — paper model vs Paper Learned A* (legacy checkpoint): N=70; 62W/0T/8L; mean expansion reduction 64.12% (negative means more expansions).
- `ood_5box_risk`: Risk-Averse Ensemble A* (kappa=1) vs Calibrated Confidence-Aware Ensemble A* (conf_50): N=92; 65W/1T/26L; mean expansion reduction 13.56% (negative means more expansions).
- `ood_7box_snapshot94`: MC Confidence-Aware A* — paper model vs Paper Learned A* (legacy checkpoint): N=70; 62W/0T/8L; mean expansion reduction 63.20% (negative means more expansions).
- `ood_7box_snapshot94`: MC-Dropout on Scratch Model #0 vs Single Scratch Model #0 A*: N=61; 4W/0T/57L; mean expansion reduction -258.48% (negative means more expansions).
- `ood_7box_snapshot94`: Risk-Averse Ensemble A* (kappa=1) vs Confidence-Aware Ensemble A* (conf_20): N=73; 52W/0T/21L; mean expansion reduction 14.60% (negative means more expansions).
- `ood_7box_snapshot94`: Risk-Averse Ensemble A* (kappa=1) vs Calibrated Confidence-Aware Ensemble A* (conf_50): N=72; 54W/1T/17L; mean expansion reduction 27.56% (negative means more expansions).

## Limitations

MC dropout is model-dependent: scratch M0 solves 93/100 five-box maps versus 77/100 for its MC variant, and also solves more seven-box maps than its MC variant (see the table). Inference-time perturbation sensitivity, altered rankings and gating interactions are hypotheses, not demonstrated causes. Disagreement has not been established as a calibrated predictor of distance error. These learned search methods do not guarantee optimal plans. “Calibrated” names a gating configuration, not statistical error calibration.
