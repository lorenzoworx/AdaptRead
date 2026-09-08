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
3. **Bounded reward:** separately testable comprehension, normalized speed,
   strain, and switch-cost terms, each clipped before weighting.

Simulation, learning, evaluation, serving, and the React demo
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

## Bounded reward walkthrough and teach-back

The reward is `comprehension + 0.5·speed − 0.35·strain − 0.15·switch_cost`.
Every component is clipped into `[0, 1]` before its weight is applied. That
keeps an outlier WPM or malformed rate from dominating learning and preserves
the explicit theoretical range `[-0.5, 1.5]`.

After this milestone, you should be able to answer:

1. Why must clipping happen before weighting?
2. Which two reward terms are benefits and which two are costs?
3. How do the weights imply the `[-0.5, 1.5]` bound?

MIT licensed.
