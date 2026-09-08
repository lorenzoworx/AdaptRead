"""Bounded, locked, session-local online learning."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from threading import Lock, RLock
from typing import Any
from uuid import uuid4

import numpy as np

from adaptread.agents.linucb import LinUCB
from adaptread.agents.ucb1 import UCB1
from adaptread.domain.actions import DEFAULT_ACTION, PRESETS, PresentationAction, UserConstraints
from adaptread.domain.reward import RewardConfig, compute_reward
from adaptread.simulator.environment import ReaderObservation

Bandit = UCB1 | LinUCB


@dataclass(slots=True)
class Session:
    id: str
    agent: Bandit
    constraints: UserConstraints
    pending_action: int
    last_context: np.ndarray
    previous_action: int | None = None
    trace: list[dict[str, Any]] = field(default_factory=list)
    lock: RLock = field(default_factory=RLock)


class SessionStore:
    def __init__(self, prototype: Bandit | None = None, *, capacity: int = 128) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.prototype = prototype or LinUCB()
        self.capacity = capacity
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = Lock()
        self.metrics = {"sessions_created": 0, "steps": 0, "update_failures": 0, "evictions": 0}

    def _clone_agent(self) -> Bandit:
        state = self.prototype.to_dict()
        return UCB1.from_dict(state) if state["agent_type"] == "ucb1" else LinUCB.from_dict(state)

    def create(self, constraints: UserConstraints) -> Session:
        agent = self._clone_agent()
        initial_observation = ReaderObservation(200.0, 0.1, 0.1, 0.5, 0.5, 0.5)
        initial_context = np.concatenate(
            (initial_observation.behavioral_features(), DEFAULT_ACTION.feature_vector())
        )
        mask = constraints.action_mask(None)
        pending = agent.act(initial_context, mask)
        session = Session(str(uuid4()), agent, constraints, pending, initial_context)
        with self._lock:
            while len(self._sessions) >= self.capacity:
                self._sessions.popitem(last=False)
                self.metrics["evictions"] += 1
            self._sessions[session.id] = session
            self.metrics["sessions_created"] += 1
        return session

    def get(self, session_id: str) -> Session:
        with self._lock:
            try:
                session = self._sessions[session_id]
            except KeyError as error:
                raise KeyError("unknown session") from error
            self._sessions.move_to_end(session_id)
            return session

    def step(self, session_id: str, telemetry: dict[str, float]) -> dict[str, Any]:
        session = self.get(session_id)
        with session.lock:
            action = PRESETS[session.pending_action]
            previous = (
                PRESETS[session.previous_action] if session.previous_action is not None else None
            )
            reward = compute_reward(
                probe_correct=telemetry["probe_correct"],
                observed_wpm=telemetry["observed_wpm"],
                regression_rate=telemetry["regression_rate"],
                pause_ratio=telemetry["pause_ratio"],
                action=action,
                previous_action=previous,
                config=RewardConfig(),
            )
            observation = ReaderObservation(**telemetry)
            next_context = np.concatenate(
                (observation.behavioral_features(), action.feature_vector())
            )
            try:
                session.agent.update(
                    session.last_context, session.pending_action, reward.total, next_context, False
                )
            except (ArithmeticError, ValueError):
                self.metrics["update_failures"] += 1
            mask = session.constraints.action_mask(action)
            next_action = session.agent.act(next_context, mask)
            exploring = session.agent.last_exploring
            value = self._value(session.agent, next_context, next_action)
            entry = {
                "step": len(session.trace) + 1,
                "observed_action": session.pending_action,
                "next_action": next_action,
                "reward": asdict(reward),
                "telemetry": telemetry,
                "exploring": exploring,
            }
            session.trace.append(entry)
            session.previous_action = session.pending_action
            session.pending_action = next_action
            session.last_context = next_context
            self.metrics["steps"] += 1
            return {
                "action_index": next_action,
                "action": PRESETS[next_action].to_dict(),
                "reward": reward.total,
                "estimated_value": value,
                "exploring": exploring,
                "explanation": self._explanation(PRESETS[next_action], exploring),
            }

    @staticmethod
    def _value(agent: Bandit, context: np.ndarray, action: int) -> float:
        if isinstance(agent, LinUCB):
            return float(agent.predictions(context, explore=False)[action])
        return float(agent.values[action])

    @staticmethod
    def _explanation(action: PresentationAction, exploring: bool) -> str:
        reason = (
            "testing an uncertain safe preset"
            if exploring
            else "using the strongest current estimate"
        )
        typography = f"{action.font_size}px {action.font_family}"
        description = f"{typography}, {action.line_spacing:g} line spacing"
        return f"{reason}: {description}"
