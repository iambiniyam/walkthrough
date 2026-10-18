"""Build a guide from ordered screenshots."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from .models import Guide, Step
from .ocr import find_callout, read_lines
from .sensitive import masks_for
from .vlm import StepWriter, build_writer

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def image_paths(paths: list[Path | str]) -> list[Path]:
    output: list[Path] = []
    for value in paths:
        path = Path(value).expanduser().resolve()
        if path.is_dir():
            output.extend(
                sorted(
                    (item for item in path.iterdir() if item.suffix.lower() in IMAGE_SUFFIXES),
                    key=lambda item: item.name.lower(),
                )
            )
        elif path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            output.append(path)
        else:
            raise FileNotFoundError(path)
    return output


def build_guide(
    paths: list[Path],
    writer: StepWriter | None = None,
    title: str = "Step-by-step guide",
    redact: bool = True,
) -> Guide:
    writer = writer or build_writer("auto")
    steps: list[Step] = []
    previous: list[str] = []
    masked = 0
    for index, path in enumerate(paths):
        image = Image.open(path)
        image.load()
        lines = read_lines(path)
        draft = writer.write(index, len(paths), image, lines, previous)
        match = find_callout(lines, draft.callout) if draft.callout else None
        masks = masks_for(lines) if redact else []
        masked += len(masks)
        steps.append(
            Step(
                number=index + 1,
                image=path.name,
                title=draft.title,
                body=draft.body,
                callout=match.text if match else draft.callout,
                bbox=match.bbox if match else None,
                image_size=(image.width, image.height),
                confidence=draft.confidence,
                masks=masks,
            )
        )
        previous.append(draft.title)
    warnings = [f"{masked} sensitive text region(s) masked in the screenshots."] if masked else []
    return Guide(
        title=title,
        summary=f"A {len(steps)}-step visual walkthrough." if steps else "No screenshots.",
        steps=steps,
        warnings=warnings,
    )
