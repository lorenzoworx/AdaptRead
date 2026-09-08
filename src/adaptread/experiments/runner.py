"""Command-line training and evaluation runner."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from adaptread.agents.linucb import LinUCB
from adaptread.agents.ucb1 import UCB1
from adaptread.domain.actions import PRESETS
from adaptread.experiments.config import ExperimentConfig, load_config
from adaptread.experiments.evaluation import evaluate_agent, run_episode
from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import HELD_OUT_PERSONAS, PERSONA_BY_ID, TRAINING_PERSONAS


def build_agent(config: ExperimentConfig, seed: int) -> UCB1 | LinUCB:
    if config.agent.type == "ucb1":
        return UCB1(len(PRESETS), exploration=config.agent.exploration, seed=seed)
    return LinUCB(
        len(PRESETS),
        context_dim=29,
        alpha=config.agent.exploration,
        ridge=config.agent.ridge,
        seed=seed,
    )


def run(config: ExperimentConfig, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = tuple(PERSONA_BY_ID[persona_id] for persona_id in config.environment.persona_ids)
    training_personas = selected or TRAINING_PERSONAS
    all_runs: list[dict[str, Any]] = []
    for seed in config.training.seeds:
        agent = build_agent(config, seed)
        rng = np.random.default_rng(seed)
        for episode in range(config.training.episodes):
            persona = training_personas[episode % len(training_personas)]
            if config.training.mixed_personas:
                persona = training_personas[int(rng.integers(len(training_personas)))]
            environment = ReaderEnvironment(
                persona, episode_length=config.environment.episode_length
            )
            run_episode(agent, environment, seed * 100_000 + episode, learn=True)
        persona_results: dict[str, Any] = {}
        for persona in (*training_personas, *HELD_OUT_PERSONAS):
            environment = ReaderEnvironment(
                persona, episode_length=config.environment.episode_length
            )
            persona_results[persona.id] = evaluate_agent(
                agent,
                environment,
                tuple(config.evaluation.seeds),
                bootstrap_samples=config.evaluation.bootstrap_samples,
            )
        all_runs.append({"training_seed": seed, "personas": persona_results})
    result = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "config_hash": config.stable_hash(),
        "resolved_config": config.model_dump(mode="json"),
        "runs": all_runs,
    }
    result_path = output_dir / f"{config.name}-{config.stable_hash()}.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    _plot_results(result, output_dir / "regret.png")
    return result


def _plot_results(result: dict[str, Any], path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    personas = list(result["runs"][0]["personas"])
    regrets = [
        float(np.mean([run["personas"][persona]["mean_regret"] for run in result["runs"]]))
        for persona in personas
    ]
    figure, axis = plt.subplots(figsize=(9, 4.5))
    axis.bar(personas, regrets, color="#6d5dfc")
    axis.set_ylabel("Mean paired regret")
    axis.set_title("AdaptRead policy regret by simulated persona")
    axis.tick_params(axis="x", rotation=25)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    run(load_config(args.config), args.output)


if __name__ == "__main__":
    main()
