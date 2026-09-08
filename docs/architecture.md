# Architecture

## Offline flow

```text
validated YAML → seeded reader environments → shared episode runner
                                           ↙          ↘
                              UCB1 / LinUCB       fixed oracle
                                           ↘          ↙
                            paired-seed evaluation + bootstrap CI
                                           ↓
                                JSON metadata + regret plot
```

Four training personas produce observable behavior under hidden fatigue and
noise. Two distinct personas remain out of training. Multiple training seeds
expose learning variance; identical evaluation seeds pair each policy with its
fixed-preset oracle.

An observation contains WPM, regressions, pauses, a comprehension probe,
segment difficulty, and normalized segment length. LinUCB prepends a bias and
appends the previous presentation's 22-value encoding for 29 total values.

Serving and client flows are intentionally deferred until their milestones.
