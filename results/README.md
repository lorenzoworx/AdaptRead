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

The matching LinUCB run lowered mean regret for all six evaluated profiles:

| Simulated profile | Mixed UCB1 | LinUCB |
|---|---:|---:|
| Typical | 1.795 | 0.691 |
| Phonological | 17.154 | 9.614 |
| Low vision | 7.218 | 5.760 |
| Audio support | 3.434 | 0.956 |
| Focus chunks (held out) | 7.072 | 4.567 |
| Large text (held out) | 6.441 | 4.993 |

This is a positive but mixed result: contextual learning helps, yet its regret
remains substantial on the two most specialized training profiles and both
held-out profiles. Nothing in this synthetic result establishes real-reader
benefit.
