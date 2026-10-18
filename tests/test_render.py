
from PIL import Image

from walkthrough.models import Guide, Step
from walkthrough.render import to_html, to_markdown, write_guide


def guide() -> Guide:
    return Guide(
        title="Export a report",
        summary="A one-step guide.",
        steps=[
            Step(
                number=1,
                image="shot.png",
                title="Open Export",
                body="Select Export.",
                callout="Export",
                bbox=(20, 20, 100, 50),
                image_size=(400, 300),
                confidence=0.8,
            )
        ],
    )


def test_markdown_contains_step_and_image():
    text = to_markdown(guide())
    assert "## 1. Open Export" in text
    assert "images/step-1.png" in text
    assert "**Select:** `Export`" in text


def test_html_is_standalone_and_escaped():
    page = to_html(guide())
    assert "<!doctype html>" in page
    assert "Open Export" in page
    assert "data:image/png" not in page


def test_write_guide_creates_bundle(tmp_path):
    source = tmp_path / "shot.png"
    Image.new("RGB", (400, 300), "white").save(source)
    outputs = write_guide(guide(), [source], tmp_path / "out")
    assert outputs["markdown"].exists()
    assert outputs["html"].exists()
    assert outputs["json"].exists()
    assert outputs["bundle"].exists()
    assert (tmp_path / "out" / "images" / "step-1.png").exists()
    assert "data:image/png" in outputs["html"].read_text()
