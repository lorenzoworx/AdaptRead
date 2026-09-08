# AdaptRead

AdaptRead is a portfolio project exploring a narrow question: how can a
contextual-bandit policy choose the next safe reading presentation from recent
observable behavior?

The project uses **simulated readers only**. It is not a clinical tool, a
human-subject study, or evidence that any presentation improves outcomes for
real readers. Synthetic personas will be explicit parameter sets used to test
software and experimental methods.

## Completed milestones

1. **Repository foundation:** Python 3.12, a `src/` package layout, locked
   dependencies, Ruff, strict mypy, pytest, MIT licensing, and GitHub Actions.
2. **Presentation domain:** immutable six-field actions, six coherent presets,
   a 22-value action encoding, and hard user constraints.

Rewards, simulation, learning, evaluation, serving, and the React demo
intentionally arrive in later commits.

## Setup

Install Python 3.12 and [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync --all-extras
uv run ruff check .
uv run mypy
uv run pytest
```

Verify that the installed package works outside the repository:

```bash
cd /tmp
uv run --project /path/to/AdaptRead python -c \
  "import adaptread; print(adaptread.__version__)"
```

## Intended architecture

```text
src/adaptread/
├── domain/
├── simulator/
├── agents/
├── experiments/
└── api/
frontend/
tests/
configs/
docs/
artifacts/
```

## Milestone 2 walkthrough and teach-back

The full six-dimension Cartesian product contains 2,160 actions. AdaptRead uses
six named presets so exploration stays understandable. `UserConstraints`
filters actions before optimization, so a disallowed setting can never be
selected merely because its expected reward is high. The preset transition
graph is tested to ensure every action remains reachable under the two-change
limit.

After this milestone, you should be able to answer:

1. Why are six curated presets preferable to exploring 2,160 combinations here?
2. Why are minimum font size and TTS permission masks instead of reward penalties?
3. What does Hamming distance measure between two presentations?

MIT licensed.
