from __future__ import annotations

import numpy as np

from adaptread.simulator.environment import ReaderEnvironment
from adaptread.simulator.personas import PERSONA_BY_ID, PERSONAS


def rollout(seed: int) -> tuple[list[np.ndarray], list[float], float]:
    environment = ReaderEnvironment(PERSONA_BY_ID["typical"], episode_length=4)
    context, _ = environment.reset(seed)
    contexts = [context]
    rewards: list[float] = []
    done = False
    while not done:
        context, reward, done, truncated, _ = environment.step(0)
        assert not truncated
        contexts.append(context)
        rewards.append(reward)
    return contexts, rewards, environment.hidden_fatigue


def test_seeded_rollouts_are_reproducible() -> None:
    left = rollout(42)
    right = rollout(42)
    for a, b in zip(left[0], right[0], strict=True):
        np.testing.assert_allclose(a, b)
    np.testing.assert_allclose(left[1], right[1])
    assert left[2] == right[2]


def test_context_is_29_dimensional_and_hides_fatigue() -> None:
    environment = ReaderEnvironment(PERSONAS[1], episode_length=2)
    context, _ = environment.reset(1)
    assert context.shape == (29,)
    environment.step(0)
    assert environment.hidden_fatigue >= 0
    assert environment.last_observation.to_dict().keys() == {
        "observed_wpm",
        "regression_rate",
        "pause_ratio",
        "probe_correct",
        "segment_difficulty",
        "segment_length",
    }


def test_termination_and_persona_splits() -> None:
    environment = ReaderEnvironment(PERSONAS[0], episode_length=2)
    environment.reset(4)
    assert environment.step(0)[2] is False
    assert environment.step(0)[2] is True
    assert len(PERSONAS) == 6
    assert len({persona.preferred_action for persona in PERSONAS}) == 6
