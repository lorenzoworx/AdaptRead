"""Shared agent contract and mask helpers."""

from __future__ import annotations

from typing import Any, Protocol, Self

import numpy as np
import numpy.typing as npt

Mask = npt.NDArray[np.bool_]
Context = npt.NDArray[np.float64]


class Agent(Protocol):
    name: str

    def act(self, context: Context, action_mask: Mask) -> int: ...

    def update(
        self,
        context: Context,
        action: int,
        reward: float,
        next_context: Context,
        terminated: bool,
    ) -> None: ...

    def set_evaluation(self, evaluation: bool) -> None: ...

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self: ...


def allowed_indices(action_mask: Mask, n_actions: int) -> npt.NDArray[np.int64]:
    mask = np.asarray(action_mask, dtype=np.bool_)
    if mask.shape != (n_actions,):
        raise ValueError(f"expected action mask shape {(n_actions,)}, got {mask.shape}")
    allowed = np.flatnonzero(mask)
    if allowed.size == 0:
        raise ValueError("action mask allows no actions")
    return allowed
