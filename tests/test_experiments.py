from __future__ import annotations

from adaptread.agents.ucb1 import UCB1
from adaptread.experiments.config import load_config
from adaptread.experiments.evaluation import bootstrap_interval, evaluate_agent, run_episode
from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import PERSONAS


def test_config_is_validated_and_stably_hashed() -> None:
    config = load_config("configs/smoke.yaml")
    assert config.stable_hash() == load_config("configs/smoke.yaml").stable_hash()


def test_evaluation_is_paired_and_frozen() -> None:
    agent = UCB1()
    environment = ReaderEnvironment(PERSONAS[0], episode_length=3)
    for seed in range(5):
        run_episode(agent, environment, seed, learn=True)
    before = agent.to_dict()
    report = evaluate_agent(agent, environment, (101, 103), bootstrap_samples=100)
    assert report["paired_seeds"] == [101, 103]
    assert agent.to_dict() == before
    assert report["mean_regret"] >= -1e-9


def test_bootstrap_interval_contains_constant() -> None:
    low, high = bootstrap_interval([3.0] * 8, samples=100)
    assert low == high == 3.0
