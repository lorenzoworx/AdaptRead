# Decisions

## Contextual bandit, not full reinforcement learning

The next presentation depends on recent observable behavior, but version one
does not claim to solve long-horizon credit assignment. A contextual bandit is
easier to inspect, more data-efficient, and proportionate to the evidence.

## Six curated presets

The full product contains 2,160 combinations, many difficult to explain or
explore safely. Six coherent presets make exhaustive fixed baselines practical.

## Hard constraints before optimization

Minimum font size, TTS permission, and the two-dimension transition limit are
filters. A reward penalty could still permit a prohibited exploratory action.

## Bounded reward

Every term is clipped before weighting. This preserves the declared
`[-0.5, 1.5]` contract and prevents telemetry outliers from dominating.

## Paired, frozen evaluation

Policy and oracle share evaluation seeds. Learning and exploration are disabled
without changing counters. Multiple training seeds, bootstrap intervals,
per-persona regret, and held-out regret remain visible even when results are
negative or mixed.
