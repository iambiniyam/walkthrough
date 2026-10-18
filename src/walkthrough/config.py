"""Local paths."""

from __future__ import annotations

import os
from pathlib import Path


def model_dir() -> Path:
    return Path(
        os.getenv(
            "WALKTHROUGH_MODEL_DIR",
            str(Path.home() / ".walkthrough" / "models" / "qwen3-vl-2b-4bit"),
        )
    )


def output_root() -> Path:
    path = Path(os.getenv("WALKTHROUGH_OUTPUT", str(Path.home() / ".walkthrough" / "out")))
    path.mkdir(parents=True, exist_ok=True)
    return path
