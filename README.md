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
4. **Reader simulator:** seeded observable behavior, latent fatigue, episode
   termination, four training personas, and two held-out personas.
5. **Baselines and episode runner:** one agent contract and one training loop
   shared by random, fixed-default, and exhaustive fixed-preset oracle agents.
6. **UCB1:** a context-free learned policy with action masks, frozen
   evaluation, deterministic tie sampling, and JSON-safe state.
7. **Mixed-reader experiment:** four specialist UCB1 policies are compared
   against one policy trained across all four training personas.

Contextual learning, reproducible evaluation, serving, and the React demo
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

## Mixed-reader experiment walkthrough

One context-free policy has a single value for each preset. When simulated
personas prefer incompatible settings, mixed training therefore learns a
compromise rather than personalization. The experiment trains specialist and
mixed policies with identical budgets, then evaluates them against fixed
oracles using the same evaluation seeds.

Run the comparison with:

```bash
uv run python -m adaptread.experiments.mixed_ucb1
```

After this milestone, you should be able to answer:

1. Why can one UCB1 policy not represent two context-dependent optima?
2. What does the specialist-versus-mixed gap demonstrate?
3. Why must both groups receive the same training budget and evaluation seeds?

MIT licensed.
