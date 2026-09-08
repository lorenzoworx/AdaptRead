from __future__ import annotations

from copy import deepcopy

import numpy as np

from adaptread.agents.ucb1 import UCB1


def test_ucb1_converges_on_controlled_problem() -> None:
    agent = UCB1(3, exploration=0.4, seed=8)
    context = np.zeros(2)
    mask = np.ones(3, dtype=np.bool_)
    rewards = [0.1, 0.9, 0.3]
    for _ in range(500):
        action = agent.act(context, mask)
        agent.update(context, action, rewards[action], context, False)
    assert int(np.argmax(agent.counts)) == 1
    agent.set_evaluation(True)
    assert agent.act(context, mask) == 1


def test_ucb1_respects_masks_and_freezes_evaluation() -> None:
    agent = UCB1(3, seed=2)
    context = np.zeros(2)
    mask = np.array([False, True, False])
    before = deepcopy(agent.to_dict())
    agent.set_evaluation(True)
    action = agent.act(context, mask)
    agent.update(context, action, 1.0, context, False)
    assert action == 1
    assert agent.to_dict() == before


def test_ucb1_json_state_roundtrip() -> None:
    agent = UCB1(3, exploration=1.3, seed=7)
    context = np.zeros(2)
    mask = np.ones(3, dtype=np.bool_)
    for reward in (0.2, 0.8, 0.4, 1.0):
        action = agent.act(context, mask)
        agent.update(context, action, reward, context, False)
    clone = UCB1.from_dict(agent.to_dict())
    np.testing.assert_array_equal(clone.counts, agent.counts)
    np.testing.assert_allclose(clone.values, agent.values)
