# Experiment results

Generated reports live here. Each report states its simulator-only scope,
resolved parameters, training seeds, paired evaluation seeds, and per-persona
results.

The first full comparison used three training seeds and five paired evaluation
seeds. Each specialist UCB1 policy reached zero mean fixed-oracle regret on its
own training persona. The single mixed policy retained mean regret of `1.795`
for typical, `17.154` for phonological, `7.218` for low-vision, and `3.434` for
audio-support profiles. This is the motivating failure: one context-free value
per action cannot express incompatible reader-specific optima.
