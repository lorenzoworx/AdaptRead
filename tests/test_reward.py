from __future__ import annotations

import numpy as np
import pytest

from adaptread.domain.actions import PresentationAction
from adaptread.domain.reward import RewardConfig, compute_reward, speed_term, strain_term


def test_reward_components_clip_before_weighting() -> None:
    config = RewardConfig()
    assert speed_term(9_999, config.target_wpm) == 1.0
    assert strain_term(5.0, -2.0) == pytest.approx(0.6)


def test_theoretical_reward_extremes_are_preserved() -> None:
    compact = PresentationAction(16, "serif", 1.4, 5, "off", "light")
    opposite = PresentationAction(28, "opendyslexic", 2.0, "full", 1.6, "dark")
    high = compute_reward(
        probe_correct=8,
        observed_wpm=9_999,
        regression_rate=-3,
        pause_ratio=-3,
        action=compact,
        previous_action=None,
    )
    low = compute_reward(
        probe_correct=-8,
        observed_wpm=-1,
        regression_rate=9,
        pause_ratio=9,
        action=compact,
        previous_action=opposite,
    )
    assert high.total == 1.5
    assert low.total == -0.5


def test_theoretical_reward_bound_randomized() -> None:
    rng = np.random.default_rng(9)
    for _ in range(500):
        current = PresentationAction(
            int(rng.choice([16, 18, 22, 28])),
            str(rng.choice(["serif", "sans", "opendyslexic"])),
            float(rng.choice([1.4, 1.6, 2.0])),
            (5, 10, 20, "full")[int(rng.integers(4))],
            ("off", 0.8, 1.0, 1.3, 1.6)[int(rng.integers(5))],
            str(rng.choice(["light", "dark", "cream"])),
        )
        result = compute_reward(
            probe_correct=float(rng.normal()),
            observed_wpm=float(rng.normal(200, 800)),
            regression_rate=float(rng.normal()),
            pause_ratio=float(rng.normal()),
            action=current,
            previous_action=None,
        )
        assert -0.5 <= result.total <= 1.5
