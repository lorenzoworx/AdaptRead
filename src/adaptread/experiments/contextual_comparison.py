"""Train and evaluate LinUCB across mixed simulated readers."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from adaptread.agents.linucb import LinUCB
from adaptread.domain.actions import PRESETS
from adaptread.experiments.evaluation import evaluate_agent, run_episode
from adaptread.experiments.mixed_ucb1 import ComparisonConfig
from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import PERSONAS, TRAINING_PERSONAS


def _train(config: ComparisonConfig, seed: int) -> LinUCB:
    agent = LinUCB(len(PRESETS), context_dim=29, alpha=0.7, ridge=1.0, seed=seed)
    rng = np.random.default_rng(seed)
    for episode in range(config.episodes):
        persona = TRAINING_PERSONAS[int(rng.integers(len(TRAINING_PERSONAS)))]
        environment = ReaderEnvironment(persona, episode_length=config.episode_length)
        run_episode(agent, environment, seed * 100_000 + episode, learn=True)
    return agent


def run_contextual_comparison(config: ComparisonConfig | None = None) -> dict[str, Any]:
    config = config or ComparisonConfig()
    runs: list[dict[str, Any]] = []
    for seed in config.training_seeds:
        agent = _train(config, seed)
        persona_results: dict[str, Any] = {}
        for persona in PERSONAS:
            environment = ReaderEnvironment(persona, episode_length=config.episode_length)
            persona_results[persona.id] = evaluate_agent(
                agent,
                environment,
                config.evaluation_seeds,
                bootstrap_samples=config.bootstrap_samples,
            )
        runs.append({"training_seed": seed, "personas": persona_results})
    return {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "scope": "simulated readers only",
        "context": {
            "behavioral_features": 7,
            "previous_action_encoding": 22,
            "total_dimensions": 29,
        },
        "config": asdict(config),
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/linucb-comparison.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = run_contextual_comparison()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
