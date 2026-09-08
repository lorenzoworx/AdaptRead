"""Disjoint LinUCB with a stable Sherman-Morrison inverse update."""

from __future__ import annotations

from typing import Any, Self

import numpy as np

from adaptread.agents.base import Context, Mask, allowed_indices
from adaptread.domain.actions import PRESETS


class LinUCB:
    name = "linucb"

    def __init__(
        self,
        n_actions: int = len(PRESETS),
        context_dim: int = 29,
        alpha: float = 0.7,
        ridge: float = 1.0,
        seed: int = 0,
    ) -> None:
        if n_actions <= 0 or context_dim <= 0 or alpha < 0 or ridge <= 0:
            raise ValueError("invalid LinUCB parameters")
        self.n_actions = n_actions
        self.context_dim = context_dim
        self.alpha = alpha
        self.ridge = ridge
        self.seed = seed
        self.A_inv = np.repeat((np.eye(context_dim) / ridge)[None, :, :], n_actions, axis=0)
        self.b = np.zeros((n_actions, context_dim), dtype=np.float64)
        self.evaluation = False
        self.last_exploring = False

    def _validate_context(self, context: Context) -> np.ndarray:
        vector = np.asarray(context, dtype=np.float64)
        if vector.shape != (self.context_dim,):
            raise ValueError(f"expected context shape {(self.context_dim,)}, got {vector.shape}")
        return vector

    def predictions(self, context: Context, *, explore: bool = True) -> np.ndarray:
        x = self._validate_context(context)
        theta = np.einsum("aij,aj->ai", self.A_inv, self.b)
        means = theta @ x
        if not explore:
            return np.asarray(means, dtype=np.float64)
        variances = np.einsum("i,aij,j->a", x, self.A_inv, x)
        return np.asarray(
            means + self.alpha * np.sqrt(np.maximum(variances, 0.0)),
            dtype=np.float64,
        )

    def act(self, context: Context, action_mask: Mask) -> int:
        allowed = allowed_indices(action_mask, self.n_actions)
        means = self.predictions(context, explore=False)
        scores = means if self.evaluation else self.predictions(context, explore=True)
        choice = int(allowed[np.argmax(scores[allowed])])
        self.last_exploring = not self.evaluation and choice != int(
            allowed[np.argmax(means[allowed])]
        )
        return choice

    def update(
        self, context: Context, action: int, reward: float, next_context: Context, terminated: bool
    ) -> None:
        del next_context, terminated
        if self.evaluation:
            return
        x = self._validate_context(context)
        inverse = self.A_inv[action]
        inverse_x = inverse @ x
        denominator = 1.0 + float(x @ inverse_x)
        self.A_inv[action] = inverse - np.outer(inverse_x, inverse_x) / denominator
        self.b[action] += reward * x

    def set_evaluation(self, evaluation: bool) -> None:
        self.evaluation = evaluation

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.name,
            "n_actions": self.n_actions,
            "context_dim": self.context_dim,
            "alpha": self.alpha,
            "ridge": self.ridge,
            "seed": self.seed,
            "A_inv": self.A_inv.tolist(),
            "b": self.b.tolist(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        agent = cls(
            int(value["n_actions"]),
            int(value["context_dim"]),
            float(value["alpha"]),
            float(value["ridge"]),
            int(value.get("seed", 0)),
        )
        agent.A_inv = np.asarray(value["A_inv"], dtype=np.float64)
        agent.b = np.asarray(value["b"], dtype=np.float64)
        if agent.A_inv.shape != (agent.n_actions, agent.context_dim, agent.context_dim):
            raise ValueError("invalid LinUCB inverse state shape")
        if agent.b.shape != (agent.n_actions, agent.context_dim):
            raise ValueError("invalid LinUCB coefficient state shape")
        return agent
