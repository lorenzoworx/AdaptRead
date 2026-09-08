# Architecture

## Offline flow

```text
validated YAML → seeded reader environments → shared episode runner
                                           ↙          ↘
                              UCB1 / LinUCB       fixed oracle
                                           ↘          ↙
                            paired-seed evaluation + bootstrap CI
                                           ↓
                         JSON metadata + regret plot + policy
```

Four training personas produce observable behavior under hidden fatigue and
noise. Two distinct personas remain out of training. Multiple training seeds
expose learning variance; identical evaluation seeds pair each policy with its
fixed-preset oracle.

An observation contains WPM, regressions, pauses, a comprehension probe,
segment difficulty, and normalized segment length. LinUCB prepends a bias and
appends the previous presentation's 22-value encoding for 29 total values.

The policy artifact stores an explicit schema version, agent type, parameters,
configuration hash, seeds, timestamp, and evaluation summary.

## Online flow

```text
versioned policy → clone per session → hard constraint mask → next action
                         ↑                                      ↓
                    local update ← bounded reward ← client telemetry
```

The base policy remains immutable. A bounded least-recently-used session store
owns one cloned agent and one lock per session. Steps for the same session
serialize; separate sessions learn independently. Traces and counters expose
behavior without persisting synthetic online state.

The client flow is deferred until its milestone.
