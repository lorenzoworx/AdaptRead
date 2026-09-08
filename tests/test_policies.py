from __future__ import annotations

import json
from pathlib import Path

import pytest

from adaptread.agents.linucb import LinUCB
from adaptread.api.policies import PolicyArtifact, load_policy, save_policy


def test_policy_schema_roundtrip(tmp_path: Path) -> None:
    artifact = PolicyArtifact.create(
        agent=LinUCB(),
        config_hash="abc123",
        seeds=[11, 29],
        evaluation_summary={"mean_regret": 1.2},
    )
    path = tmp_path / "policy.json"
    save_policy(artifact, path)
    loaded = load_policy(path)
    assert loaded.schema_version == 1
    assert loaded.config_hash == "abc123"
    assert loaded.build_agent().context_dim == 29


def test_malformed_policy_version_is_rejected(tmp_path: Path) -> None:
    artifact = PolicyArtifact.create(
        agent=LinUCB(), config_hash="abc", seeds=[1], evaluation_summary={}
    )
    path = tmp_path / "policy.json"
    save_policy(artifact, path)
    raw = json.loads(path.read_text())
    raw["schema_version"] = 999
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="schema version"):
        load_policy(path)


def test_policy_path_traversal_and_non_json_files_are_rejected() -> None:
    with pytest.raises(ValueError, match="traversal"):
        load_policy(Path("safe") / ".." / "policy.json")
    with pytest.raises(ValueError, match="JSON"):
        load_policy(Path("policy.pkl"))
