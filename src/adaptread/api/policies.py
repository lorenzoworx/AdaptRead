"""Versioned, JSON-only policy persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from adaptread.agents.base import Agent
from adaptread.agents.linucb import LinUCB
from adaptread.agents.ucb1 import UCB1

SCHEMA_VERSION = 1


class PolicyArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int = SCHEMA_VERSION
    agent_type: str
    created_at: str
    parameters: dict[str, Any]
    config_hash: str
    seeds: list[int] = Field(default_factory=list)
    evaluation_summary: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        agent: Agent,
        config_hash: str,
        seeds: list[int],
        evaluation_summary: dict[str, Any],
    ) -> PolicyArtifact:
        state = agent.to_dict()
        return cls(
            agent_type=str(state["agent_type"]),
            created_at=datetime.now(UTC).isoformat(),
            parameters=state,
            config_hash=config_hash,
            seeds=seeds,
            evaluation_summary=evaluation_summary,
        )

    def build_agent(self) -> UCB1 | LinUCB:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported policy schema version {self.schema_version}")
        if self.agent_type == "ucb1":
            return UCB1.from_dict(self.parameters)
        if self.agent_type == "linucb":
            return LinUCB.from_dict(self.parameters)
        raise ValueError(f"unsupported agent type {self.agent_type!r}")


def _safe_json_path(path: Path) -> Path:
    if path.suffix != ".json" or path.name in {"", ".", ".."}:
        raise ValueError("policy path must name a JSON file")
    if any(part == ".." for part in path.parts):
        raise ValueError("policy path traversal is not allowed")
    return path


def save_policy(artifact: PolicyArtifact, path: str | Path) -> None:
    target = _safe_json_path(Path(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(artifact.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_policy(path: str | Path) -> PolicyArtifact:
    target = _safe_json_path(Path(path))
    raw = json.loads(target.read_text(encoding="utf-8"))
    artifact = PolicyArtifact.model_validate(raw)
    if artifact.schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported policy schema version {artifact.schema_version}")
    artifact.build_agent()
    return artifact
