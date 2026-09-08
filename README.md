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
8. **Contextual LinUCB:** one ridge-regression model per preset uses a
   documented 29-dimensional context and Sherman–Morrison inverse updates.
9. **Reproducible evaluation:** validated YAML, multiple training seeds,
   paired evaluation seeds, bootstrap intervals, held-out regret, and plots.

Policy artifacts, serving, and the React demo intentionally arrive in later
commits.

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

## Reproducible evaluation walkthrough

Experiment YAML rejects unknown fields and resolves into a hashed configuration.
Each algorithm trains under multiple seeds. Evaluation clones and freezes the
policy, uses the same seeds for policy and oracle, reports per-persona regret,
and bootstraps a 95% interval. The resolved config is stored beside every run.

Run the comparison with:

```bash
uv run adaptread-experiment configs/portfolio.yaml --output results/portfolio
```

After this milestone, you should be able to answer:

1. Why are policy and oracle evaluated with paired seeds?
2. What uncertainty does the bootstrap interval represent?
3. Why must evaluation freeze exploration, updates, and counters?

MIT licensed.
