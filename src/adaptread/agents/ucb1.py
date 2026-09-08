"""Context-free UCB1 with masks, frozen evaluation, and JSON-safe state."""

from __future__ import annotations

from typing import Any, Self

import numpy as np

from adaptread.agents.base import Context, Mask, allowed_indices
from adaptread.domain.actions import PRESETS


class UCB1:
    name = "ucb1"

    def __init__(
        self, n_actions: int = len(PRESETS), exploration: float = 2.0, seed: int = 0
    ) -> None:
        if n_actions <= 0 or exploration < 0:
            raise ValueError("invalid UCB1 parameters")
        self.n_actions = n_actions
        self.exploration = exploration
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.counts = np.zeros(n_actions, dtype=np.int64)
        self.values = np.zeros(n_actions, dtype=np.float64)
        self.evaluation = False
        self.last_exploring = False

    def scores(self) -> np.ndarray:
        total = max(1, int(self.counts.sum()))
        bonus = np.full(self.n_actions, np.inf)
        seen = self.counts > 0
        bonus[seen] = np.sqrt(self.exploration * np.log(total + 1.0) / self.counts[seen])
        return np.asarray(self.values + bonus, dtype=np.float64)

    def act(self, context: Context, action_mask: Mask) -> int:
        del context
        allowed = allowed_indices(action_mask, self.n_actions)
        if self.evaluation:
            choice = int(allowed[np.argmax(self.values[allowed])])
            self.last_exploring = False
            return choice
        untried = allowed[self.counts[allowed] == 0]
        if untried.size:
            choice = int(self.rng.choice(untried))
            self.last_exploring = True
            return choice
        scores = self.scores()
        choice = int(allowed[np.argmax(scores[allowed])])
        self.last_exploring = choice != int(allowed[np.argmax(self.values[allowed])])
        return choice

    def update(
        self, context: Context, action: int, reward: float, next_context: Context, terminated: bool
    ) -> None:
        del context, next_context, terminated
        if self.evaluation:
            return
        self.counts[action] += 1
        self.values[action] += (reward - self.values[action]) / self.counts[action]

    def set_evaluation(self, evaluation: bool) -> None:
        self.evaluation = evaluation

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.name,
            "n_actions": self.n_actions,
            "exploration": self.exploration,
            "seed": self.seed,
            "counts": self.counts.tolist(),
            "values": self.values.tolist(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        agent = cls(int(value["n_actions"]), float(value["exploration"]), int(value.get("seed", 0)))
        agent.counts = np.asarray(value["counts"], dtype=np.int64)
        agent.values = np.asarray(value["values"], dtype=np.float64)
        if agent.counts.shape != (agent.n_actions,) or agent.values.shape != (agent.n_actions,):
            raise ValueError("invalid UCB1 state shape")
        return agent
