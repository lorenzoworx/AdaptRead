"""Minimal production/hosted deployment smoke test."""

from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def fetch(url: str, *, data: dict[str, object] | None = None) -> dict[str, object]:
    body = json.dumps(data).encode() if data is not None else None
    request = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=30) as response:  # noqa: S310
        return json.load(response)  # type: ignore[no-any-return]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    assert fetch(f"{base}/healthz")["status"] == "ok"
    session = fetch(f"{base}/v1/sessions", data={})
    assert session["simulated_only"] is True
    print("AdaptRead deployment smoke test passed")


if __name__ == "__main__":
    main()
