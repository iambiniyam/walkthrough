from PIL import Image

from walkthrough.models import Step
from walkthrough.ocr import TextLine
from walkthrough.pipeline import build_guide
from walkthrough.render import annotate
from walkthrough.sensitive import is_sensitive, masks_for
from walkthrough.vlm import HeuristicWriter


def test_sensitive_patterns():
    assert is_sensitive("Email: jane@example.com")
    assert is_sensitive("Card: 4111 1111 1111 1111")
    assert is_sensitive("SSN: 123-45-6789")
    assert is_sensitive("IBAN: GB82WEST12345698765432")
    assert is_sensitive("Phone: +1 555 123 4567")
    assert not is_sensitive("Continue")
    assert not is_sensitive("Version 2.0")


def test_masks_for_lines():
    lines = [
        TextLine("Email: jane@example.com", (10, 10, 120, 30)),
        TextLine("Continue", (10, 50, 80, 70)),
    ]
    assert masks_for(lines) == [(10, 10, 120, 30)]


def test_build_guide_masks_and_can_disable(tmp_path, monkeypatch):
    image_path = tmp_path / "shot.png"
    Image.new("RGB", (400, 300), "white").save(image_path)
    lines = [
        TextLine("Email: jane@example.com", (20, 20, 200, 45)),
        TextLine("Continue", (20, 100, 120, 125)),
    ]
    monkeypatch.setattr("walkthrough.pipeline.read_lines", lambda path: lines)
    masked = build_guide([image_path], writer=HeuristicWriter(), redact=True)
    assert masked.steps[0].masks == [(20, 20, 200, 45)]
    assert masked.warnings
    plain = build_guide([image_path], writer=HeuristicWriter(), redact=False)
    assert plain.steps[0].masks == []
    assert not plain.warnings


def test_annotate_draws_mask(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (100, 100), "white").save(source)
    target = tmp_path / "out.png"
    step = Step(
        number=1,
        image="source.png",
        title="Step",
        body="Body",
        masks=[(10.0, 10.0, 40.0, 20.0)],
    )
    annotate(source, step, target)
    assert Image.open(target).getpixel((20, 15)) == (20, 20, 20)
