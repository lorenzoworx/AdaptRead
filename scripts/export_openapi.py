"""Export FastAPI's schema for TypeScript generation."""

from __future__ import annotations

import json
from pathlib import Path

from adaptread.api.app import app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    (project_root / "openapi.json").write_text(
        json.dumps(app.openapi(), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
