"""Simple baselines sharing the production agent interface."""

from __future__ import annotations

from typing import Any, Self

import numpy as np

from adaptread.agents.base import Context, Mask, allowed_indices
from adaptread.domain.actions import PRESETS
from adaptread.simulator.environment import ReaderEnvironment


class RandomAgent:
    name = "random"

    def __init__(self, n_actions: int = len(PRESETS), seed: int = 0) -> None:
        self.n_actions = n_actions
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def act(self, context: Context, action_mask: Mask) -> int:
        del context
        return int(self.rng.choice(allowed_indices(action_mask, self.n_actions)))

    def update(
        self, context: Context, action: int, reward: float, next_context: Context, terminated: bool
    ) -> None:
        del context, action, reward, next_context, terminated

    def set_evaluation(self, evaluation: bool) -> None:
        del evaluation

    def to_dict(self) -> dict[str, Any]:
        return {"agent_type": self.name, "n_actions": self.n_actions, "seed": self.seed}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        return cls(int(value["n_actions"]), int(value.get("seed", 0)))


class DefaultAgent(RandomAgent):
    name = "default"

    def act(self, context: Context, action_mask: Mask) -> int:
        del context
        allowed = allowed_indices(action_mask, self.n_actions)
        return 0 if action_mask[0] else int(allowed[0])


class FixedOracleAgent(DefaultAgent):
    """Exhaustively selects the best fixed preset for a known simulator."""

    name = "fixed_oracle"

    def __init__(self, action: int, n_actions: int = len(PRESETS)) -> None:
        super().__init__(n_actions=n_actions)
        self.action = action

    def act(self, context: Context, action_mask: Mask) -> int:
        del context
        return (
            self.action
            if action_mask[self.action]
            else int(allowed_indices(action_mask, self.n_actions)[0])
        )

    def to_dict(self) -> dict[str, Any]:
        return {"agent_type": self.name, "n_actions": self.n_actions, "action": self.action}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        return cls(int(value["action"]), int(value["n_actions"]))

    @classmethod
    def for_environment(cls, environment: ReaderEnvironment, seeds: tuple[int, ...]) -> Self:
        means: list[float] = []
        for action in range(len(PRESETS)):
            totals: list[float] = []
            for seed in seeds:
                context, _ = environment.reset(seed)
                total = 0.0
                done = False
                while not done:
                    mask = environment.action_mask()
                    selected = action if mask[action] else int(np.flatnonzero(mask)[0])
                    context, reward, done, _, _ = environment.step(selected)
                    total += reward
                totals.append(total)
            means.append(float(np.mean(totals)))
        return cls(int(np.argmax(means)))
