#!/usr/bin/env python3
"""Launch the Solara visualization (single server process, no reload loop)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "viz" / "app.py"


def main() -> None:
    port = os.environ.get("PORT", "8765")
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Open http://{host}:{port} in your browser")
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "solara",
            "run",
            f"{APP}:Page",
            "--host",
            host,
            "--port",
            port,
        ],
    )


if __name__ == "__main__":
    main()
