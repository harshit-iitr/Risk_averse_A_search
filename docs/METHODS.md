# Methods and hyperparameters

Each method scores candidate Sokoban states and uses a priority queue to choose
the next state to expand. `g(s)` denotes accumulated path cost.

## Percentile guidance

Each predictor maintains its own online score history. Its output is mapped to
a percentile `p_m(s)` before aggregation. The mean is `mu_p`, the population
variance is `v_p`, and the standard deviation is `sigma_p = sqrt(v_p)`.
The classical minimum-Manhattan-matching heuristic is also mapped to a
percentile, `p_classical`. Separate histories make the ranks invariant to
constant offsets between predictors.

## Confidence-aware search

The priority blends learned and classical guidance:

```text
f = g + 50 * (lambda * mu_p + (1 - lambda) * p_classical)
```

MC confidence uses five stochastic passes through one model:

```text
lambda = 0.20 + 0.80 * max(0, 1 - 4 * v_p)
```

The confidence ensemble uses five trained members:

```text
lambda = lambda_min + (1 - lambda_min) * max(0, 1 - 2.5 * sigma_p)
```

`conf_20` sets `lambda_min=0.20`; `conf_50` sets `lambda_min=0.50`.
Both retain `C=50`. The fixed hybrid uses `lambda=0.50` throughout.

## Risk-aware search

```text
f = g + 50 * min(1, mu_p + kappa * sigma_p)
kappa = 1.0
```

The disagreement term adds a search-time penalty to the state priority.
The network weights stay fixed during evaluation. The clipped rank lies in
`[0, 1]`, and A* selects the smallest priority from the open queue.

## Parameter table

| Setting | MC confidence-aware | Confidence ensemble | Risk-aware ensemble |
|---|---|---|---|
| Predictions per state | 5 stochastic passes | 5 trained models | 5 trained models |
| Inference dropout | 0.10 | Disabled | Disabled |
| Heuristic scale C | 50 | 50 | 50 |
| Learned-weight floor | 0.20 | 0.20 / 0.50 | — |
| Disagreement sensitivity | 4 on variance | 2.5 on standard deviation | — |
| Risk strength κ | — | — | 1.0 |
| Uncertainty space | Per-pass percentiles | Per-member percentiles | Per-member percentiles |

All example evaluations reuse the included checkpoints. The optional training
utility is `tools/train_deep_ensemble.py`; it supports per-member sampling of
80% of the training set without replacement. Training is separate from the
reproduction commands.
