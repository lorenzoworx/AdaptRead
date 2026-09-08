# AdaptRead

AdaptRead is a portfolio project exploring a narrow question: how can a
contextual-bandit policy choose the next safe reading presentation from recent
observable behavior?

The project uses **simulated readers only**. It is not a clinical tool, a
human-subject study, or evidence that any presentation improves outcomes for
real readers. Synthetic personas will be explicit parameter sets used to test
software and experimental methods.

## Milestone 1: repository foundation

This first milestone establishes a clean Python 3.12 project with a `src/`
package layout, locked dependencies, Ruff, strict mypy, pytest, an MIT license,
and GitHub Actions. Presentation actions, rewards, simulation, learning,
evaluation, serving, and the React demo intentionally arrive in later commits.

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

## Walkthrough and teach-back

The `src/` layout prevents accidental imports from the working directory and
makes the clean-install check meaningful. Python 3.12 is aligned across local
development and CI. The lockfile makes dependency resolution reproducible.

After this milestone, you should be able to answer:

1. Why does a `src/` layout catch packaging mistakes that a flat layout can hide?
2. Which four checks define the initial quality gate?
3. What claim does the simulator-only scope explicitly avoid?

MIT licensed.
