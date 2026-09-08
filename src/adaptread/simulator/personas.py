"""Synthetic reader parameters; these are not medical or human-subject claims."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from adaptread.domain.actions import PresentationAction


@dataclass(frozen=True, slots=True)
class Persona:
    id: str
    label: str
    preferred_action: PresentationAction
    base_wpm: float
    comprehension_bias: float
    fatigue_rate: float
    recovery_rate: float

    def fit(self, action: PresentationAction) -> float:
        return 1.0 - action.distance(self.preferred_action) / 6.0


PERSONAS: tuple[Persona, ...] = (
    Persona("typical", "Typical reader", PresentationAction(), 250.0, 0.8, 0.035, 0.05),
    Persona(
        "phonological",
        "Phonological decoding profile",
        PresentationAction(22, "opendyslexic", 1.6, 20, "off", "cream"),
        135.0,
        0.25,
        0.075,
        0.035,
    ),
    Persona(
        "low_vision",
        "Low-vision presentation profile",
        PresentationAction(28, "sans", 1.6, 20, "off", "dark"),
        120.0,
        0.2,
        0.06,
        0.04,
    ),
    Persona(
        "audio_support",
        "Audio-support profile",
        PresentationAction(18, "sans", 1.6, 20, 1.0, "light"),
        175.0,
        0.45,
        0.05,
        0.04,
    ),
    Persona(
        "focus_held_out",
        "Focus-chunk profile (held out)",
        PresentationAction(18, "sans", 1.6, 10, "off", "light"),
        205.0,
        0.55,
        0.045,
        0.05,
    ),
    Persona(
        "large_text_held_out",
        "Large-text profile (held out)",
        PresentationAction(22, "sans", 1.6, 20, "off", "light"),
        165.0,
        0.4,
        0.055,
        0.04,
    ),
)
TRAINING_PERSONAS = PERSONAS[:4]
HELD_OUT_PERSONAS = PERSONAS[4:]
PERSONA_BY_ID = {persona.id: persona for persona in PERSONAS}


def logistic(value: float) -> float:
    return float(1.0 / (1.0 + np.exp(-np.clip(value, -30.0, 30.0))))
