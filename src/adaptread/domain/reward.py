"""Bounded and independently testable reading reward."""

from __future__ import annotations

from dataclasses import dataclass

from adaptread.domain.actions import PresentationAction


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


@dataclass(frozen=True, slots=True)
class RewardConfig:
    comprehension_weight: float = 1.0
    speed_weight: float = 0.5
    strain_weight: float = 0.35
    switch_weight: float = 0.15
    target_wpm: float = 250.0


@dataclass(frozen=True, slots=True)
class RewardBreakdown:
    comprehension: float
    normalized_speed: float
    strain: float
    switch_cost: float
    total: float


def comprehension_term(probe_correct: bool | float) -> float:
    return _clip(float(probe_correct))


def speed_term(observed_wpm: float, target_wpm: float) -> float:
    if target_wpm <= 0:
        raise ValueError("target_wpm must be positive")
    return _clip(observed_wpm / target_wpm)


def strain_term(regression_rate: float, pause_ratio: float) -> float:
    return _clip(0.6 * _clip(regression_rate) + 0.4 * _clip(pause_ratio))


def switch_term(current: PresentationAction, previous: PresentationAction | None) -> float:
    return 0.0 if previous is None else _clip(current.distance(previous) / 6.0)


def compute_reward(
    *,
    probe_correct: bool | float,
    observed_wpm: float,
    regression_rate: float,
    pause_ratio: float,
    action: PresentationAction,
    previous_action: PresentationAction | None,
    config: RewardConfig | None = None,
) -> RewardBreakdown:
    config = config or RewardConfig()
    comprehension = comprehension_term(probe_correct)
    speed = speed_term(observed_wpm, config.target_wpm)
    strain = strain_term(regression_rate, pause_ratio)
    switching = switch_term(action, previous_action)
    total = (
        config.comprehension_weight * comprehension
        + config.speed_weight * speed
        - config.strain_weight * strain
        - config.switch_weight * switching
    )
    return RewardBreakdown(comprehension, speed, strain, switching, total)
