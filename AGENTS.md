# Project scope

Support exactly the ten method IDs in `src/methods.py`. Do not add algorithms
or result rows without an explicit user request. Preserve the selected existing
checkpoints and per-map observations. Never invent missing experiment combinations.

# Ranking heuristics

Ranking models have arbitrary scalar offsets. Compute uncertainty in each
member's percentile space, never from raw cross-model variance. Disagreement
is a search signal, not a demonstrated Gaussian interval over physical distance.
Retain both the confidence-gated and risk-aware formulations used in the results.

# Evidence

Seven-box reporting currently stops at maps 1–82. Maps 46–82 have completed
live-log summaries, not downloaded action plans. Paper Learned GBFS has only
five seven-box attempts. Keep these limitations explicit. Do not silently
combine differing devices or stopping budgets. Retain independent plan replay
and resumable output for future experiments. Keep all credentials out of Git.
