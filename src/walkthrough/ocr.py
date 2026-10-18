"""OCR and callout lookup."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True, slots=True)
class TextLine:
    text: str
    bbox: tuple[float, float, float, float]
    confidence: float = 1.0


@lru_cache(maxsize=1)
def _engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def read_lines(path: Path | str) -> list[TextLine]:
    image = np.asarray(Image.open(path).convert("RGB"))[:, :, ::-1]
    result, _elapsed = _engine()(image)
    lines: list[TextLine] = []
    for item in result or []:
        box, text, score = item[0], str(item[1]), float(item[2])
        if not text.strip() or score < 0.5:
            continue
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        lines.append(
            TextLine(text, (min(xs), min(ys), max(xs), max(ys)), score)
        )
    return sorted(lines, key=lambda line: (line.bbox[1], line.bbox[0]))


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def find_callout(lines: list[TextLine], text: str) -> TextLine | None:
    wanted = normalize(text)
    if not wanted:
        return None
    exact = [line for line in lines if normalize(line.text) == wanted]
    if exact:
        return exact[0]
    contained = [line for line in lines if wanted in normalize(line.text)]
    if contained:
        return min(contained, key=lambda line: len(line.text))
    partial = [line for line in lines if normalize(line.text) in wanted]
    if partial:
        return max(partial, key=lambda line: len(line.text))
    return None
