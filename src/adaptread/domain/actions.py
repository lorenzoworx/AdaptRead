"""Safe, deliberately small presentation action space."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Self

import numpy as np

FONT_SIZES = (16, 18, 22, 28)
FONT_FAMILIES = ("serif", "sans", "opendyslexic")
LINE_SPACINGS = (1.4, 1.6, 2.0)
CHUNK_SIZES: tuple[int | str, ...] = (5, 10, 20, "full")
TTS_RATES: tuple[str | float, ...] = ("off", 0.8, 1.0, 1.3, 1.6)
THEMES = ("light", "dark", "cream")
DIMENSION_VALUES: tuple[tuple[Any, ...], ...] = (
    FONT_SIZES,
    FONT_FAMILIES,
    LINE_SPACINGS,
    CHUNK_SIZES,
    TTS_RATES,
    THEMES,
)
ACTION_FEATURE_DIM = sum(len(values) for values in DIMENSION_VALUES)


@dataclass(frozen=True, slots=True)
class PresentationAction:
    """An immutable reading presentation spanning six controlled dimensions."""

    font_size: int = 18
    font_family: str = "sans"
    line_spacing: float = 1.6
    chunk_size: int | str = 20
    tts_rate: str | float = "off"
    theme: str = "light"

    def __post_init__(self) -> None:
        values = self.to_tuple()
        for name, value, allowed in zip(
            self.dimension_names(), values, DIMENSION_VALUES, strict=True
        ):
            if value not in allowed:
                raise ValueError(f"unsupported {name}: {value!r}")

    @staticmethod
    def dimension_names() -> tuple[str, ...]:
        return ("font_size", "font_family", "line_spacing", "chunk_size", "tts_rate", "theme")

    def to_tuple(self) -> tuple[Any, ...]:
        return (
            self.font_size,
            self.font_family,
            self.line_spacing,
            self.chunk_size,
            self.tts_rate,
            self.theme,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        return cls(**value)

    def distance(self, other: PresentationAction) -> int:
        """Return the Hamming distance between two presentation settings."""
        return sum(
            left != right for left, right in zip(self.to_tuple(), other.to_tuple(), strict=True)
        )

    def feature_vector(self) -> np.ndarray:
        """Return the documented 22-value concatenated one-hot encoding."""
        encoded: list[float] = []
        for value, allowed in zip(self.to_tuple(), DIMENSION_VALUES, strict=True):
            encoded.extend(float(value == candidate) for candidate in allowed)
        return np.asarray(encoded, dtype=np.float64)


DEFAULT_ACTION = PresentationAction()
PRESETS: tuple[PresentationAction, ...] = (
    DEFAULT_ACTION,
    PresentationAction(22, "sans", 1.6, 20, "off", "light"),
    PresentationAction(18, "sans", 1.6, 10, "off", "light"),
    PresentationAction(18, "sans", 1.6, 20, 1.0, "light"),
    PresentationAction(22, "opendyslexic", 1.6, 20, "off", "cream"),
    PresentationAction(28, "sans", 1.6, 20, "off", "dark"),
)
PRESET_NAMES = ("default", "large", "focus", "audio", "dyslexia-support", "low-vision")


@dataclass(frozen=True, slots=True)
class UserConstraints:
    """Hard safety rules. Disallowed actions never reach an agent or simulator."""

    min_font_size: int = 16
    tts_allowed: bool = True
    max_changed_dimensions: int = 2

    def __post_init__(self) -> None:
        if self.min_font_size not in FONT_SIZES:
            raise ValueError("minimum font size must be a supported font size")
        if not 0 <= self.max_changed_dimensions <= 6:
            raise ValueError("max_changed_dimensions must be between 0 and 6")

    def allows(
        self, action: PresentationAction, previous_action: PresentationAction | None
    ) -> bool:
        if action.font_size < self.min_font_size:
            return False
        if not self.tts_allowed and action.tts_rate != "off":
            return False
        return (
            previous_action is None
            or action.distance(previous_action) <= self.max_changed_dimensions
        )

    def action_mask(
        self,
        previous_action: PresentationAction | None,
        actions: tuple[PresentationAction, ...] = PRESETS,
    ) -> np.ndarray:
        return np.asarray(
            [self.allows(action, previous_action) for action in actions], dtype=np.bool_
        )
