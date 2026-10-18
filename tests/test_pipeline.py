from pathlib import Path

from PIL import Image

from walkthrough.ocr import TextLine
from walkthrough.pipeline import build_guide, image_paths
from walkthrough.vlm import HeuristicWriter


def make_image(path: Path, size=(400, 300)) -> Path:
    Image.new("RGB", size, "white").save(path)
    return path


def test_image_paths_sorts_folder(tmp_path):
    make_image(tmp_path / "02.png")
    make_image(tmp_path / "01.png")
    assert [path.name for path in image_paths([tmp_path])] == ["01.png", "02.png"]


def test_build_guide_uses_visible_labels(tmp_path, monkeypatch):
    first = make_image(tmp_path / "one.png")
    second = make_image(tmp_path / "two.png")
    monkeypatch.setattr(
        "walkthrough.pipeline.read_lines",
        lambda path: [TextLine("Export", (20, 20, 100, 50), 0.9), TextLine("Settings", (20, 80, 120, 110), 0.9)],
    )
    guide = build_guide([first, second], writer=HeuristicWriter(), title="Export a report")
    assert len(guide.steps) == 2
    assert guide.steps[0].callout == "Export"
    assert guide.steps[0].bbox == (20, 20, 100, 50)
    assert guide.steps[0].image_size == (400, 300)
    assert guide.title == "Export a report"
