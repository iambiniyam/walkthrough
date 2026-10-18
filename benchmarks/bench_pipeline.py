"""Measure OCR and guide-building time on a folder of screenshots."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from walkthrough.pipeline import build_guide, image_paths
from walkthrough.vlm import build_writer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path, nargs="?", default=Path("examples"))
    parser.add_argument("--model", default="heuristic")
    args = parser.parse_args()
    paths = image_paths([args.folder])
    writer = build_writer(args.model)
    started = time.perf_counter()
    guide = build_guide(paths, writer=writer, title="Benchmark")
    elapsed = time.perf_counter() - started
    print(
        {
            "steps": len(guide.steps),
            "writer": writer.name,
            "seconds": round(elapsed, 2),
            "ms_per_step": round(elapsed / max(1, len(guide.steps)) * 1000),
        }
    )


if __name__ == "__main__":
    main()
