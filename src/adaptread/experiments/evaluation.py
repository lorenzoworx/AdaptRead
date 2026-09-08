"""Shared training loop, paired evaluation, regret, and confidence intervals."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import numpy as np

from adaptread.agents.base import Agent
from adaptread.agents.baselines import FixedOracleAgent
from adaptread.domain.actions import PRESETS
from adaptread.simulator.environment import ReaderEnvironment


@dataclass(slots=True)
class EpisodeResult:
    total_reward: float
    mean_comprehension: float
    action_counts: list[int]
    switches: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_reward": self.total_reward,
            "mean_comprehension": self.mean_comprehension,
            "action_counts": self.action_counts,
            "switches": self.switches,
        }


def run_episode(
    agent: Agent, environment: ReaderEnvironment, seed: int, *, learn: bool
) -> EpisodeResult:
    context, _ = environment.reset(seed)
    agent.set_evaluation(not learn)
    total = 0.0
    probes: list[float] = []
    counts = [0] * len(PRESETS)
    switches = 0
    previous: int | None = None
    terminated = False
    while not terminated:
        mask = environment.action_mask()
        action = agent.act(context, mask)
        next_context, reward, terminated, _, info = environment.step(action)
        if learn:
            agent.update(context, action, reward, next_context, terminated)
        total += reward
        probes.append(float(info["reward"]["comprehension"]))
        counts[action] += 1
        switches += int(previous is not None and previous != action)
        previous = action
        context = next_context
    return EpisodeResult(total, float(np.mean(probes)), counts, switches)


def bootstrap_interval(
    values: Iterable[float], *, samples: int = 2_000, confidence: float = 0.95, seed: int = 0
) -> tuple[float, float]:
    data = np.asarray(list(values), dtype=np.float64)
    if data.size == 0:
        raise ValueError("cannot bootstrap an empty sample")
    rng = np.random.default_rng(seed)
    means = np.mean(rng.choice(data, size=(samples, data.size), replace=True), axis=1)
    tail = (1.0 - confidence) / 2.0
    return float(np.quantile(means, tail)), float(np.quantile(means, 1.0 - tail))


def evaluate_agent(
    agent: Agent,
    environment: ReaderEnvironment,
    seeds: tuple[int, ...],
    *,
    bootstrap_samples: int = 2_000,
) -> dict[str, Any]:
    frozen = deepcopy(agent)
    oracle = FixedOracleAgent.for_environment(deepcopy(environment), seeds)
    rewards: list[float] = []
    regrets: list[float] = []
    episodes: list[dict[str, Any]] = []
    for seed in seeds:
        result = run_episode(frozen, environment, seed, learn=False)
        oracle_result = run_episode(oracle, environment, seed, learn=False)
        rewards.append(result.total_reward)
        regrets.append(oracle_result.total_reward - result.total_reward)
        episodes.append(result.to_dict())
    low, high = bootstrap_interval(rewards, samples=bootstrap_samples)
    return {
        "mean_reward": float(np.mean(rewards)),
        "reward_ci_95": [low, high],
        "mean_regret": float(np.mean(regrets)),
        "paired_seeds": list(seeds),
        "oracle_action": oracle.action,
        "episodes": episodes,
    }
