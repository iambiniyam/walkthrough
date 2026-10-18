"""Explainable screenshot ordering from OCR action words."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .ocr import TextLine, read_lines

ACTIONS: dict[str, int] = {
    "sign in": 0,
    "log in": 0,
    "create account": 0,
    "start": 0,
    "open": 1,
    "select": 1,
    "choose": 1,
    "continue": 2,
    "next": 2,
    "proceed": 2,
    "save": 3,
    "export": 3,
    "submit": 3,
    "apply": 3,
    "confirm": 4,
    "download": 4,
    "done": 5,
    "finish": 5,
    "close": 5,
}


def action_rank(lines: list[TextLine]) -> int | None:
    ranks = [
        rank
        for line in lines
        for phrase, rank in ACTIONS.items()
        if phrase in line.text.casefold()
    ]
    return min(ranks) if ranks else None


def order_paths(
    paths: list[Path],
    reader: Callable[[Path], list[TextLine]] = read_lines,
) -> list[Path]:
    """Sort by the earliest action word, keeping input when evidence is weak."""
    ranked = [(path, action_rank(reader(path))) for path in paths]
    known = {rank for _, rank in ranked if rank is not None}
    if len(known) < 2:
        return list(paths)
    return [
        path
        for _index, (path, _rank) in sorted(
            enumerate(ranked),
            key=lambda item: (
                item[1][1] is None,
                item[1][1] if item[1][1] is not None else 99,
                item[0],
            ),
        )
    ]
