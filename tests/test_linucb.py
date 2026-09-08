from __future__ import annotations

from copy import deepcopy

import numpy as np

from adaptread.agents.linucb import LinUCB
from adaptread.experiments.contextual_comparison import run_contextual_comparison
from adaptread.experiments.mixed_ucb1 import ComparisonConfig


def test_sherman_morrison_matches_direct_inverse() -> None:
    rng = np.random.default_rng(15)
    agent = LinUCB(2, context_dim=5, ridge=1.7)
    direct = [1.7 * np.eye(5) for _ in range(2)]
    for _ in range(50):
        context = rng.normal(size=5)
        action = int(rng.integers(2))
        agent.update(context, action, float(rng.normal()), context, False)
        direct[action] += np.outer(context, context)
    for action in range(2):
        np.testing.assert_allclose(agent.A_inv[action], np.linalg.inv(direct[action]), atol=1e-10)


def test_linucb_json_roundtrip_and_frozen_state() -> None:
    agent = LinUCB(3, context_dim=4)
    context = np.array([1.0, 0.2, 0.4, 0.8])
    agent.update(context, 1, 0.8, context, False)
    clone = LinUCB.from_dict(agent.to_dict())
    np.testing.assert_allclose(clone.A_inv, agent.A_inv)
    clone.set_evaluation(True)
    before = deepcopy(clone.to_dict())
    clone.update(context, 1, 3.0, context, False)
    assert clone.to_dict() == before


def test_linucb_can_choose_different_actions_for_different_contexts() -> None:
    agent = LinUCB(2, context_dim=2, alpha=0.0)
    left = np.array([1.0, 0.0])
    right = np.array([0.0, 1.0])
    for _ in range(20):
        agent.update(left, 0, 1.0, left, False)
        agent.update(left, 1, 0.0, left, False)
        agent.update(right, 0, 0.0, right, False)
        agent.update(right, 1, 1.0, right, False)
    agent.set_evaluation(True)
    mask = np.ones(2, dtype=np.bool_)
    assert agent.act(left, mask) == 0
    assert agent.act(right, mask) == 1


def test_contextual_comparison_records_29_dimensions_and_held_out_results() -> None:
    report = run_contextual_comparison(
        ComparisonConfig(
            episodes=4,
            episode_length=3,
            training_seeds=(5,),
            evaluation_seeds=(41, 43),
            bootstrap_samples=100,
        )
    )
    assert report["context"]["total_dimensions"] == 29
    assert "focus_held_out" in report["runs"][0]["personas"]
