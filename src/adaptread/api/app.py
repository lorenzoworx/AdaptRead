"""FastAPI application for adaptive, session-local reading policies."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException
from fastapi import Path as ApiPath
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from adaptread import __version__
from adaptread.agents.linucb import LinUCB
from adaptread.api.policies import load_policy
from adaptread.api.sessions import SessionStore
from adaptread.domain.actions import DIMENSION_VALUES, PRESET_NAMES, PRESETS, UserConstraints
from adaptread.simulator.personas import HELD_OUT_PERSONAS, PERSONAS, TRAINING_PERSONAS


class ConstraintInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_font_size: int = 16
    tts_allowed: bool = True
    max_changed_dimensions: int = Field(default=2, ge=0, le=6)


class SessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    constraints: ConstraintInput = ConstraintInput()


class TelemetryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observed_wpm: float = Field(ge=0.0, le=1_500.0)
    regression_rate: float = Field(ge=0.0, le=1.0)
    pause_ratio: float = Field(ge=0.0, le=1.0)
    probe_correct: float = Field(ge=0.0, le=1.0)
    segment_difficulty: float = Field(ge=0.0, le=1.0)
    segment_length: float = Field(ge=0.0, le=1.0)


def _load_prototype() -> LinUCB:
    candidates = (
        Path(__file__).resolve().parents[3] / "artifacts" / "default-linucb.json",
        Path("/app/artifacts/default-linucb.json"),
    )
    for path in candidates:
        if path.is_file():
            agent = load_policy(path).build_agent()
            if isinstance(agent, LinUCB):
                return agent
    return LinUCB()


store = SessionStore(_load_prototype())
app = FastAPI(
    title="AdaptRead API",
    version=__version__,
    description="Contextual-bandit presentation service backed by simulated-reader experiments.",
)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return "\n".join(f"adaptread_{key} {value}" for key, value in store.metrics.items()) + "\n"


@app.get("/v1/policies")
def policies() -> list[dict[str, Any]]:
    return [{"id": "linucb-v1", "agent_type": "linucb", "schema_version": 1, "context_dim": 29}]


@app.get("/v1/simulator")
def simulator() -> dict[str, Any]:
    return {
        "scope": "simulated readers only; no real-user efficacy claims",
        "dimension_values": [list(values) for values in DIMENSION_VALUES],
        "presets": [action.to_dict() for action in PRESETS],
        "preset_names": PRESET_NAMES,
        "personas": [
            {
                "id": persona.id,
                "label": persona.label,
                "split": "training" if persona in TRAINING_PERSONAS else "held_out",
                "base_wpm": persona.base_wpm,
                "preferred_action": persona.preferred_action.to_dict(),
                "comprehension_bias": persona.comprehension_bias,
                "fatigue_rate": persona.fatigue_rate,
                "recovery_rate": persona.recovery_rate,
            }
            for persona in PERSONAS
        ],
        "held_out_count": len(HELD_OUT_PERSONAS),
    }


@app.post("/v1/sessions", status_code=201)
def create_session(request: SessionInput) -> dict[str, Any]:
    try:
        constraints = UserConstraints(**request.constraints.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    session = store.create(constraints)
    return {
        "session_id": session.id,
        "action_index": session.pending_action,
        "action": PRESETS[session.pending_action].to_dict(),
        "simulated_only": True,
    }


@app.post("/v1/sessions/{session_id}/step")
def step_session(
    request: TelemetryInput,
    session_id: Annotated[str, ApiPath(min_length=1, max_length=100)],
) -> dict[str, Any]:
    try:
        return store.step(session_id, request.model_dump())
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/v1/sessions/{session_id}/trace")
def session_trace(
    session_id: Annotated[str, ApiPath(min_length=1, max_length=100)],
) -> dict[str, Any]:
    try:
        session = store.get(session_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    with session.lock:
        return {"session_id": session.id, "steps": list(session.trace)}


def _mount_frontend() -> None:
    candidates = (
        Path(__file__).resolve().parents[3] / "frontend" / "dist",
        Path("/app/frontend/dist"),
    )
    for directory in candidates:
        if directory.is_dir():
            app.mount("/", StaticFiles(directory=directory, html=True), name="frontend")
            return


_mount_frontend()


def run() -> None:
    import uvicorn

    uvicorn.run("adaptread.api.app:app", host="0.0.0.0", port=8000)
