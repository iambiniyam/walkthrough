"""Command line interface for walkthrough."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .config import model_dir
from .models import Guide
from .order import order_paths
from .pipeline import build_guide, image_paths
from .render import render_existing, write_guide
from .vlm import build_writer

app = typer.Typer(help="Turn ordered screenshots into a step-by-step guide.", no_args_is_help=True)
console = Console()


@app.callback(invoke_without_command=True)
def _root(
    version: bool = typer.Option(False, "--version", is_eager=True, help="Show the version and exit."),
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()



@app.command()
def build(
    paths: list[Path] = typer.Argument(..., exists=True),
    out: Path = typer.Option(Path("walkthrough-out"), "--out", "-o"),
    title: str = typer.Option("Step-by-step guide", "--title"),
    model: str = typer.Option("auto", "--model", help="auto, qwen, or heuristic"),
    redact: bool = typer.Option(True, "--redact/--no-redact", help="Mask emails, phones, cards, and IDs."),
    auto_order: bool = typer.Option(False, "--auto-order", help="Sort by likely action words before building."),
) -> None:
    """Build a guide from screenshots or a folder."""
    sources = image_paths([str(path) for path in paths])
    if not sources:
        raise typer.Exit("no images found")
    if auto_order:
        sources = order_paths(sources)
        console.print("ordered screenshots by OCR action words")
    writer = build_writer(model)
    console.print(f"building {len(sources)} steps with {writer.name}")
    guide = build_guide(sources, writer=writer, title=title, redact=redact)
    outputs = write_guide(guide, sources, out)
    console.print(f"wrote {outputs['markdown']}")
    console.print(f"wrote {outputs['html']}")
    console.print(f"wrote {outputs['bundle']}")


@app.command("render")
def render_command(
    guide_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    out: Path = typer.Option(Path("walkthrough-rendered"), "--out", "-o"),
    images: Path | None = typer.Option(None, "--images", help="Folder with step-N.png images."),
) -> None:
    """Re-render an edited guide JSON with its existing images."""
    try:
        guide = Guide.from_dict(json.loads(guide_path.read_text(encoding="utf-8")))
    except (ValueError, TypeError) as exc:
        raise typer.BadParameter(f"invalid guide JSON: {exc}") from exc
    base = images or guide_path.parent / "images"
    sources: list[Path] = []
    for step in guide.steps:
        candidates = [
            base / f"step-{step.number}.png",
            base / Path(step.image).name if step.image else base / f"step-{step.number}.png",
            guide_path.parent / step.image if step.image else guide_path.parent,
        ]
        found = next((path for path in candidates if path.is_file()), None)
        if found is None:
            raise typer.BadParameter(f"image for step {step.number} not found under {base}")
        sources.append(found)
    outputs = render_existing(guide, sources, out)
    console.print(f"wrote {outputs['markdown']}")
    console.print(f"wrote {outputs['html']}")
    console.print(f"wrote {outputs['bundle']}")


@app.command()
def serve(port: int = typer.Option(8792, "--port")) -> None:
    """Start the local web UI."""
    import uvicorn

    uvicorn.run("walkthrough.server:app", host="127.0.0.1", port=port, log_level="warning")


@app.command()
def doctor() -> None:
    """Check the model and runtime."""
    folder = model_dir()
    ready = (folder / "model.safetensors").exists()
    console.print("model: [bold]qwen3-vl-2b-4bit[/bold]")
    console.print(f"path: {folder}")
    console.print(f"weights: {'ready' if ready else 'missing'}")
    if not ready:
        console.print("Run: [bold]python scripts/download_model.py[/bold]")
    console.print("[green]ready[/green]")


if __name__ == "__main__":
    app()
