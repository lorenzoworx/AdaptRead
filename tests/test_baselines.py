from __future__ import annotations

import numpy as np

from adaptread.agents.baselines import DefaultAgent, FixedOracleAgent, RandomAgent
from adaptread.domain.actions import PRESETS, UserConstraints
from adaptread.experiments.evaluation import run_episode
from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import PERSONA_BY_ID


def test_shared_runner_records_required_episode_metrics() -> None:
    environment = ReaderEnvironment(PERSONA_BY_ID["typical"], episode_length=5)
    result = run_episode(DefaultAgent(), environment, seed=7, learn=False)
    assert sum(result.action_counts) == 5
    assert result.action_counts[0] == 5
    assert 0.0 <= result.mean_comprehension <= 1.0
    assert result.switches == 0
    assert isinstance(result.total_reward, float)


def test_random_agent_respects_action_mask() -> None:
    agent = RandomAgent(seed=4)
    context = np.zeros(29)
    mask = UserConstraints(min_font_size=28, tts_allowed=False).action_mask(None)
    choices = {agent.act(context, mask) for _ in range(30)}
    assert choices
    assert all(mask[choice] for choice in choices)


def test_exhaustive_fixed_oracle_is_no_worse_than_default() -> None:
    seeds = (11, 13, 17)
    environment = ReaderEnvironment(PERSONA_BY_ID["low_vision"], episode_length=8)
    oracle = FixedOracleAgent.for_environment(environment, seeds)
    oracle_mean = np.mean(
        [run_episode(oracle, environment, seed, learn=False).total_reward for seed in seeds]
    )
    default = DefaultAgent(len(PRESETS))
    default_mean = np.mean(
        [run_episode(default, environment, seed, learn=False).total_reward for seed in seeds]
    )
    assert oracle_mean >= default_mean
