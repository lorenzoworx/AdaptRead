from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from adaptread.domain.actions import DEFAULT_ACTION, PRESETS, PresentationAction, UserConstraints


def test_action_conversion_distance_and_features() -> None:
    action = PresentationAction(22, "sans", 2.0, 10, 1.0, "cream")
    assert PresentationAction.from_dict(action.to_dict()) == action
    assert action.distance(DEFAULT_ACTION) == 5
    vector = action.feature_vector()
    assert vector.shape == (22,)
    assert vector.sum() == 6
    with pytest.raises(FrozenInstanceError):
        action.font_size = 18  # type: ignore[misc]


def test_constraints_are_authoritative() -> None:
    constraints = UserConstraints(min_font_size=22, tts_allowed=False, max_changed_dimensions=2)
    assert not constraints.allows(DEFAULT_ACTION, None)
    assert constraints.allows(PRESETS[1], None)
    assert not constraints.allows(PRESETS[3], None)
    assert constraints.action_mask(None).tolist() == [False, True, False, False, True, True]


def test_safe_preset_transition_graph_is_connected() -> None:
    constraints = UserConstraints()
    reached = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for index, allowed in enumerate(constraints.action_mask(PRESETS[current])):
            if allowed and index not in reached:
                reached.add(index)
                frontier.append(index)
    assert reached == set(range(len(PRESETS)))


def test_invalid_action_and_constraint_values_fail_closed() -> None:
    with pytest.raises(ValueError, match="unsupported font_size"):
        PresentationAction(font_size=17)
    with pytest.raises(ValueError, match="minimum font size"):
        UserConstraints(min_font_size=17)
