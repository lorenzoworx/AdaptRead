"""Motivating experiment: specialist UCB1 policies versus one mixed policy."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from adaptread.agents.ucb1 import UCB1
from adaptread.domain.actions import PRESETS
from adaptread.experiments.evaluation import evaluate_agent, run_episode
from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import PERSONAS, TRAINING_PERSONAS, Persona


@dataclass(frozen=True, slots=True)
class ComparisonConfig:
    episodes: int = 80
    episode_length: int = 30
    training_seeds: tuple[int, ...] = (11, 29, 47)
    evaluation_seeds: tuple[int, ...] = (101, 103, 107, 109, 113)
    exploration: float = 2.0
    bootstrap_samples: int = 2_000


def _train(personas: tuple[Persona, ...], config: ComparisonConfig, seed: int) -> UCB1:
    agent = UCB1(len(PRESETS), exploration=config.exploration, seed=seed)
    rng = np.random.default_rng(seed)
    for episode in range(config.episodes):
        persona = personas[int(rng.integers(len(personas)))]
        environment = ReaderEnvironment(persona, episode_length=config.episode_length)
        run_episode(agent, environment, seed * 100_000 + episode, learn=True)
    return agent


def run_comparison(config: ComparisonConfig | None = None) -> dict[str, Any]:
    config = config or ComparisonConfig()
    runs: list[dict[str, Any]] = []
    for seed in config.training_seeds:
        mixed = _train(TRAINING_PERSONAS, config, seed)
        specialists = {
            persona.id: _train((persona,), config, seed) for persona in TRAINING_PERSONAS
        }
        mixed_results: dict[str, Any] = {}
        specialist_results: dict[str, Any] = {}
        for persona in PERSONAS:
            environment = ReaderEnvironment(persona, episode_length=config.episode_length)
            mixed_results[persona.id] = evaluate_agent(
                mixed,
                environment,
                config.evaluation_seeds,
                bootstrap_samples=config.bootstrap_samples,
            )
            if persona.id in specialists:
                specialist_results[persona.id] = evaluate_agent(
                    specialists[persona.id],
                    environment,
                    config.evaluation_seeds,
                    bootstrap_samples=config.bootstrap_samples,
                )
        runs.append(
            {
                "training_seed": seed,
                "mixed": mixed_results,
                "specialists": specialist_results,
            }
        )
    return {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "scope": "simulated readers only",
        "config": asdict(config),
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/ucb1-mixed-comparison.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(run_comparison(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
