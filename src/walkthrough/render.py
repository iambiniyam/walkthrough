"""Annotate screenshots and render Markdown, HTML, and a bundle."""

from __future__ import annotations

import base64
import html
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import Guide


def annotate(source: Path, step, output: Path) -> Path:
    image = Image.open(source).convert("RGB")
    draw = ImageDraw.Draw(image)
    for x0, y0, x1, y1 in step.masks:
        pad = max(2, round(image.width * 0.003))
        draw.rectangle((x0 - pad, y0 - pad, x1 + pad, y1 + pad), fill=(20, 20, 20))
    if step.bbox:
        x0, y0, x1, y1 = step.bbox
        pad = max(4, round(image.width * 0.006))
        box = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
        width = max(3, round(image.width * 0.004))
        draw.rounded_rectangle(box, radius=8, outline=(198, 40, 40), width=width)
        radius = max(14, round(image.width * 0.016))
        center = (box[0] + radius, box[1] + radius)
        draw.ellipse(
            (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
            fill=(198, 40, 40),
        )
        try:
            font = ImageFont.truetype("Helvetica.ttc", radius + 2)
        except OSError:
            font = ImageFont.load_default()
        text = str(step.number)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        draw.text(
            (center[0] - (right - left) / 2, center[1] - (bottom - top) / 2 - 1),
            text,
            fill="white",
            font=font,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def to_markdown(guide: Guide, image_dir: str = "images") -> str:
    lines = [f"# {guide.title}", "", guide.summary, ""]
    for step in guide.steps:
        lines.append(f"## {step.number}. {step.title}")
        lines.append("")
        lines.append(f"![Step {step.number}: {step.title}]({image_dir}/step-{step.number}.png)")
        lines.append("")
        lines.append(step.body)
        if step.callout:
            lines.append("")
            lines.append(f"**Select:** `{step.callout}`")
        lines.append("")
    return "\n".join(lines)


def _data_uri(path: Path) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def to_html(guide: Guide, images: list[Path] | None = None) -> str:
    cards = []
    for index, step in enumerate(guide.steps):
        image = ""
        if images and index < len(images):
            image = f'<img src="{_data_uri(images[index])}" alt="Step {step.number}: {html.escape(step.title)}">'
        callout = (
            f'<p class="callout"><strong>Select:</strong> <code>{html.escape(step.callout)}</code></p>'
            if step.callout
            else ""
        )
        cards.append(
            f'<section class="step"><div class="number">{step.number}</div>'
            f'<div class="content"><h2>{html.escape(step.title)}</h2>{image}'
            f'<p>{html.escape(step.body)}</p>{callout}</div></section>'
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(guide.title)}</title>
<style>
:root {{ color-scheme: light dark; --ink:#17211b; --muted:#5d6a61; --line:#ddd7c6; --paper:#f7f5ef; --accent:#b3261e; }}
@media (prefers-color-scheme: dark) {{ :root {{ --ink:#edf2ee; --muted:#a7b5ac; --line:#2d3a33; --paper:#101613; --accent:#ff8a80; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:ui-sans-serif,system-ui,-apple-system,sans-serif; line-height:1.6; }}
main {{ width:min(880px,100% - 32px); margin:0 auto; padding:48px 0; }}
h1 {{ font-size:2rem; letter-spacing:-.02em; margin:0 0 4px; }}
.summary {{ color:var(--muted); margin:0 0 32px; }}
.step {{ display:grid; grid-template-columns:40px minmax(0,1fr); gap:16px; padding:20px 0; border-top:1px solid var(--line); }}
.number {{ display:grid; place-items:center; width:32px; height:32px; border-radius:50%; background:var(--accent); color:#fff; font-weight:700; }}
h2 {{ font-size:1.125rem; margin:0 0 8px; }}
img {{ display:block; max-width:100%; height:auto; border:1px solid var(--line); border-radius:12px; margin:8px 0 12px; }}
.callout {{ background:#fdecea; color:#5f1510; border-radius:8px; padding:8px 12px; display:inline-block; }}
@media (prefers-color-scheme: dark) {{ .callout {{ background:#3a1f1c; color:#ffd9d4; }} }}
code {{ font-family:ui-monospace,Menlo,monospace; }}
.toolbar {{ display:flex; justify-content:flex-end; margin-bottom:20px; }}
.print {{ border:1px solid var(--line); border-radius:8px; background:transparent; color:var(--ink); padding:10px 16px; font:inherit; font-weight:600; cursor:pointer; }}
.print:hover {{ border-color:var(--accent); }}
@media print {{
  .toolbar {{ display:none; }}
  body {{ background:#fff; color:#111; }}
  main {{ width:100%; padding:0; }}
  .step {{ break-inside:avoid; border-color:#ccc; }}
  .callout {{ background:#f2f2f2; color:#111; }}
  img {{ max-height:70vh; object-fit:contain; }}
}}
</style></head>
<body><main><div class="toolbar"><button class="print" type="button" onclick="window.print()">Print / Save as PDF</button></div><h1>{html.escape(guide.title)}</h1><p class="summary">{html.escape(guide.summary)}</p>
{''.join(cards)}
</main></body></html>"""


def _write_outputs(guide: Guide, images: list[Path], out_dir: Path) -> dict[str, Path]:
    markdown = out_dir / "guide.md"
    markdown.write_text(to_markdown(guide), encoding="utf-8")
    page = out_dir / "guide.html"
    page.write_text(to_html(guide, images), encoding="utf-8")
    payload = out_dir / "guide.json"
    payload.write_text(json.dumps(guide.to_dict(), indent=2), encoding="utf-8")
    bundle = out_dir / "guide.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(markdown, "guide.md")
        archive.write(page, "guide.html")
        archive.write(payload, "guide.json")
        for image in images:
            archive.write(image, f"images/{image.name}")
    return {"json": payload, "markdown": markdown, "html": page, "bundle": bundle}


def write_guide(guide: Guide, sources: list[Path], out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"
    images_dir.mkdir(exist_ok=True)
    annotated: list[Path] = []
    for source, step in zip(sources, guide.steps):
        target = images_dir / f"step-{step.number}.png"
        annotate(source, step, target)
        annotated.append(target)
        step.image = f"images/step-{step.number}.png"
    return _write_outputs(guide, annotated, out_dir)


def render_existing(guide: Guide, sources: list[Path], out_dir: Path) -> dict[str, Path]:
    """Render an edited guide JSON using existing numbered images."""
    if len(sources) != len(guide.steps):
        raise ValueError(f"expected {len(guide.steps)} images, got {len(sources)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"
    images_dir.mkdir(exist_ok=True)
    images: list[Path] = []
    for source, step in zip(sources, guide.steps):
        target = images_dir / f"step-{step.number}.png"
        if source.resolve() != target.resolve():
            if source.suffix.lower() == ".png":
                target.write_bytes(source.read_bytes())
            else:
                Image.open(source).convert("RGB").save(target, format="PNG")
        images.append(target)
        step.image = f"images/step-{step.number}.png"
    return _write_outputs(guide, images, out_dir)
