"""Seeded partially observable reader simulation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from adaptread.domain.actions import DEFAULT_ACTION, PRESETS, PresentationAction, UserConstraints
from adaptread.domain.reward import RewardConfig, compute_reward
from adaptread.simulator.personas import Persona, logistic


@dataclass(frozen=True, slots=True)
class ReaderObservation:
    observed_wpm: float
    regression_rate: float
    pause_ratio: float
    probe_correct: float
    segment_difficulty: float
    segment_length: float

    def behavioral_features(self) -> np.ndarray:
        """Seven features: bias plus six observable values, never latent fatigue."""
        return np.asarray(
            [
                1.0,
                np.clip(self.observed_wpm / 300.0, 0.0, 1.5),
                np.clip(self.regression_rate, 0.0, 1.0),
                np.clip(self.pause_ratio, 0.0, 1.0),
                np.clip(self.probe_correct, 0.0, 1.0),
                np.clip(self.segment_difficulty, 0.0, 1.0),
                np.clip(self.segment_length, 0.0, 1.0),
            ],
            dtype=np.float64,
        )

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


class ReaderEnvironment:
    """Gymnasium-style simulator with observable behavior and hidden fatigue."""

    def __init__(
        self,
        persona: Persona,
        *,
        episode_length: int = 30,
        constraints: UserConstraints | None = None,
        reward_config: RewardConfig | None = None,
    ) -> None:
        if episode_length <= 0:
            raise ValueError("episode_length must be positive")
        self.persona = persona
        self.episode_length = episode_length
        self.constraints = constraints or UserConstraints()
        self.reward_config = reward_config or RewardConfig()
        self._rng = np.random.default_rng(0)
        self._fatigue = 0.0
        self._step = 0
        self.previous_action: PresentationAction | None = None
        self.last_observation = ReaderObservation(0.0, 0.0, 0.0, 0.0, 0.5, 0.5)

    @property
    def hidden_fatigue(self) -> float:
        """Exposed for tests/diagnostics, not included in agent context."""
        return self._fatigue

    def reset(self, seed: int | None = None) -> tuple[np.ndarray, dict[str, Any]]:
        self._rng = np.random.default_rng(seed)
        self._fatigue = 0.0
        self._step = 0
        self.previous_action = None
        self.last_observation = ReaderObservation(
            observed_wpm=self.persona.base_wpm,
            regression_rate=0.1,
            pause_ratio=0.1,
            probe_correct=0.5,
            segment_difficulty=float(self._rng.uniform(0.2, 0.8)),
            segment_length=float(self._rng.uniform(0.2, 0.8)),
        )
        return self.context(DEFAULT_ACTION), {"persona_id": self.persona.id}

    def context(self, previous_action: PresentationAction | None = None) -> np.ndarray:
        action = previous_action or self.previous_action or DEFAULT_ACTION
        return np.concatenate(
            (self.last_observation.behavioral_features(), action.feature_vector())
        )

    def action_mask(self) -> np.ndarray:
        return self.constraints.action_mask(self.previous_action)

    def step(self, action_index: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if not 0 <= action_index < len(PRESETS):
            raise IndexError("action index out of range")
        action = PRESETS[action_index]
        if not self.constraints.allows(action, self.previous_action):
            raise ValueError("action violates user constraints")
        difficulty = float(self._rng.uniform(0.15, 0.95))
        length = float(self._rng.uniform(0.15, 1.0))
        fit = self.persona.fit(action)
        load = np.clip(difficulty * (1.1 - fit) + 0.45 * self._fatigue, 0.0, 1.0)
        p_correct = logistic(self.persona.comprehension_bias + 2.2 * fit - 2.4 * load)
        probe = float(self._rng.random() < p_correct)
        wpm_noise = float(self._rng.lognormal(mean=0.0, sigma=0.08))
        wpm = self.persona.base_wpm * (0.72 + 0.42 * fit) * (1.0 - 0.38 * self._fatigue) * wpm_noise
        regression = float(np.clip(0.05 + 0.5 * load + self._rng.normal(0.0, 0.025), 0.0, 1.0))
        pause = float(np.clip(0.03 + 0.42 * load + self._rng.normal(0.0, 0.02), 0.0, 1.0))
        rest = max(0.0, 1.0 - load)
        self._fatigue = float(
            np.clip(
                self._fatigue
                + self.persona.fatigue_rate * load
                - self.persona.recovery_rate * rest,
                0.0,
                1.0,
            )
        )
        reward = compute_reward(
            probe_correct=probe,
            observed_wpm=wpm,
            regression_rate=regression,
            pause_ratio=pause,
            action=action,
            previous_action=self.previous_action,
            config=self.reward_config,
        )
        self.previous_action = action
        self.last_observation = ReaderObservation(wpm, regression, pause, probe, difficulty, length)
        self._step += 1
        terminated = self._step >= self.episode_length
        info: dict[str, Any] = {
            "observation": self.last_observation.to_dict(),
            "reward": asdict(reward),
            "action": action.to_dict(),
        }
        return self.context(action), reward.total, terminated, False, info
