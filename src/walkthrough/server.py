"""Local web interface for walkthrough."""

from __future__ import annotations

import shutil
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from .config import output_root
from .pipeline import IMAGE_SUFFIXES, build_guide
from .render import write_guide
from .vlm import build_writer

STATIC = Path(__file__).resolve().parent / "static"
MAX_UPLOAD = 12 * 1024 * 1024
MAX_FILES = 20
Image.MAX_IMAGE_PIXELS = 40_000_000

app = FastAPI(title="walkthrough", version="0.1.4")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
writer = build_writer("auto")
lock = threading.Lock()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html", media_type="text/html")


@app.get("/healthz")
def health() -> dict[str, object]:
    return {"ok": True, "writer": writer.name}


@app.post("/api/build")
async def build(
    files: list[UploadFile] = File(...),
    title: str = Form("Step-by-step guide"),
    redact: bool = Form(True),
) -> JSONResponse:
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"too many screenshots (max {MAX_FILES})")
    job = uuid.uuid4().hex
    folder = output_root() / job
    sources_dir = folder / "source"
    sources_dir.mkdir(parents=True, exist_ok=True)
    sources: list[Path] = []
    for index, upload in enumerate(files):
        suffix = Path(upload.filename or "shot").suffix.lower()
        if suffix not in IMAGE_SUFFIXES:
            raise HTTPException(status_code=400, detail=f"unsupported image: {upload.filename}")
        payload = await upload.read(MAX_UPLOAD + 1)
        if len(payload) > MAX_UPLOAD:
            raise HTTPException(status_code=413, detail=f"{upload.filename}: image too large (max 12 MB)")
        target = sources_dir / f"{index:02d}{suffix}"
        target.write_bytes(payload)
        try:
            image = Image.open(target)
            image.load()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"{upload.filename}: not a readable image") from exc
        sources.append(target)

    try:
        with lock:
            guide = build_guide(
                sources,
                writer=writer,
                title=title.strip() or "Step-by-step guide",
                redact=redact,
            )
        outputs = write_guide(guide, sources, folder)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        shutil.rmtree(sources_dir, ignore_errors=True)

    payload = guide.to_dict()
    for step in payload["steps"]:
        step["image_url"] = f"/files/{job}/{step['image']}"
    return JSONResponse(
        {
            "job": job,
            "writer": writer.name,
            "guide": payload,
            "downloads": {
                "bundle": f"/files/{job}/{outputs['bundle'].name}",
                "html": f"/files/{job}/{outputs['html'].name}",
                "markdown": f"/files/{job}/{outputs['markdown'].name}",
                "json": f"/files/{job}/{outputs['json'].name}",
            },
        }
    )


@app.get("/files/{job}/{name:path}")
def download(job: str, name: str) -> FileResponse:
    folder = (output_root() / Path(job).name).resolve()
    target = (folder / name).resolve()
    if not target.is_relative_to(folder) or not target.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(target)
