"""Command line interface for walkthrough."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .config import model_dir
from .pipeline import build_guide, image_paths
from .render import write_guide
from .vlm import build_writer

app = typer.Typer(help="Turn ordered screenshots into a step-by-step guide.", no_args_is_help=True)
console = Console()


@app.command()
def build(
    paths: list[Path] = typer.Argument(..., exists=True),
    out: Path = typer.Option(Path("walkthrough-out"), "--out", "-o"),
    title: str = typer.Option("Step-by-step guide", "--title"),
    model: str = typer.Option("auto", "--model", help="auto, qwen, or heuristic"),
) -> None:
    """Build a guide from screenshots or a folder."""
    sources = image_paths([str(path) for path in paths])
    if not sources:
        raise typer.Exit("no images found")
    writer = build_writer(model)
    console.print(f"building {len(sources)} steps with {writer.name}")
    guide = build_guide(sources, writer=writer, title=title)
    outputs = write_guide(guide, sources, out)
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
