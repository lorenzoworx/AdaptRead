"""Validated YAML configuration for reproducible experiments."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class EnvironmentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    episode_length: int = Field(default=30, ge=1, le=10_000)
    persona_ids: list[str] = Field(default_factory=lambda: ["typical"])


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["ucb1", "linucb"] = "linucb"
    exploration: float = Field(default=0.7, ge=0.0)
    ridge: float = Field(default=1.0, gt=0.0)


class TrainingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    episodes: int = Field(default=80, ge=1)
    seeds: list[int] = Field(default_factory=lambda: [11, 29, 47])
    mixed_personas: bool = True


class EvaluationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seeds: list[int] = Field(default_factory=lambda: [101, 103, 107, 109, 113])
    bootstrap_samples: int = Field(default=2_000, ge=100)
    confidence: float = Field(default=0.95, gt=0.0, lt=1.0)


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = "contextual-comparison"
    environment: EnvironmentConfig = EnvironmentConfig()
    agent: AgentConfig = AgentConfig()
    training: TrainingConfig = TrainingConfig()
    evaluation: EvaluationConfig = EvaluationConfig()

    def stable_hash(self) -> str:
        payload = self.model_dump_json(exclude_none=False)
        return sha256(payload.encode()).hexdigest()[:12]


def load_config(path: str | Path) -> ExperimentConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return ExperimentConfig.model_validate(raw)
