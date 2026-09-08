from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest
from fastapi.testclient import TestClient

from adaptread.agents.linucb import LinUCB
from adaptread.api.app import app
from adaptread.api.sessions import SessionStore
from adaptread.domain.actions import UserConstraints

client = TestClient(app)
TELEMETRY = {
    "observed_wpm": 210.0,
    "regression_rate": 0.12,
    "pause_ratio": 0.08,
    "probe_correct": 1.0,
    "segment_difficulty": 0.4,
    "segment_length": 0.5,
}


def test_health_session_step_trace_and_metrics() -> None:
    assert client.get("/healthz").json()["status"] == "ok"
    created = client.post("/v1/sessions", json={}).json()
    session_id = created["session_id"]
    response = client.post(f"/v1/sessions/{session_id}/step", json=TELEMETRY)
    assert response.status_code == 200
    assert response.json()["action"]["font_size"] >= 16
    assert isinstance(response.json()["explanation"], str)
    trace = client.get(f"/v1/sessions/{session_id}/trace").json()
    assert len(trace["steps"]) == 1
    assert "adaptread_steps" in client.get("/metrics").text


def test_sessions_clone_policy_isolate_and_update_online() -> None:
    store = SessionStore(LinUCB(), capacity=3)
    first = store.create(UserConstraints())
    second = store.create(UserConstraints())
    second_before = second.agent.to_dict()
    first_b_before = first.agent.b.copy()
    store.step(first.id, TELEMETRY)
    assert second.agent.to_dict() == second_before
    assert not np.array_equal(first.agent.b, first_b_before)


def test_concurrent_steps_for_one_session_are_serialized() -> None:
    store = SessionStore(capacity=2)
    session = store.create(UserConstraints())
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _: store.step(session.id, TELEMETRY), range(12)))
    assert [entry["step"] for entry in store.get(session.id).trace] == list(range(1, 13))


def test_store_evicts_least_recently_used_session_at_capacity() -> None:
    store = SessionStore(capacity=1)
    first = store.create(UserConstraints())
    second = store.create(UserConstraints())
    with pytest.raises(KeyError, match="unknown session"):
        store.get(first.id)
    assert store.get(second.id).id == second.id
    assert store.metrics["evictions"] == 1


def test_validation_and_unknown_session() -> None:
    invalid = client.post("/v1/sessions", json={"constraints": {"min_font_size": 17}})
    assert invalid.status_code == 422
    assert client.post("/v1/sessions/missing/step", json=TELEMETRY).status_code == 404
