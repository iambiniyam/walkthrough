from pathlib import Path

from walkthrough.ocr import TextLine
from walkthrough.order import action_rank, order_paths


def line(text: str) -> TextLine:
    return TextLine(text, (0, 0, 10, 10))


def test_action_rank_uses_earliest_action():
    assert action_rank([line("Continue"), line("Save")]) == 2
    assert action_rank([line("Download")]) == 4
    assert action_rank([line("Reports")]) is None


def test_order_paths_sorts_ranked_and_keeps_unknown_last():
    paths = [Path("download.png"), Path("start.png"), Path("reports.png"), Path("save.png")]
    lines = {
        Path("download.png"): [line("Download")],
        Path("start.png"): [line("Sign in")],
        Path("reports.png"): [line("Reports")],
        Path("save.png"): [line("Save")],
    }
    assert [path.name for path in order_paths(paths, reader=lambda path: lines[path])] == [
        "start.png",
        "save.png",
        "download.png",
        "reports.png",
    ]


def test_order_paths_preserves_weak_evidence():
    paths = [Path("b.png"), Path("a.png")]
    lines = {path: [line("Dashboard")] for path in paths}
    assert order_paths(paths, reader=lambda path: lines[path]) == paths
