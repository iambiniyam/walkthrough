"""Step writers: deterministic fallback and local Qwen3-VL."""

from __future__ import annotations

import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image

from .config import model_dir
from .ocr import TextLine


@dataclass(frozen=True, slots=True)
class StepDraft:
    title: str
    body: str
    callout: str = ""
    confidence: float = 0.0


class StepWriter(Protocol):
    name: str

    def write(
        self,
        index: int,
        total: int,
        image: Image.Image,
        lines: list[TextLine],
        previous: list[str],
    ) -> StepDraft: ...


ACTION_WORDS = (
    "continue",
    "next",
    "save",
    "export",
    "submit",
    "sign in",
    "log in",
    "open",
    "settings",
    "download",
    "create",
    "add",
    "confirm",
    "apply",
    "send",
    "start",
)


class HeuristicWriter:
    name = "heuristic"

    def write(self, index, total, image, lines, previous) -> StepDraft:
        labels = [line.text for line in lines if len(line.text) > 2]
        callout = next(
            (label for label in labels if any(word in label.lower() for word in ACTION_WORDS)),
            labels[0] if labels else "",
        )
        if callout:
            title = f"Select {callout}"
            body = f"Choose {callout} to continue."
        else:
            title = f"Step {index + 1}"
            body = "Review this screen before continuing."
        return StepDraft(title=title, body=body, callout=callout, confidence=0.25)


PROMPT = """You are writing one step in a software guide. Return one JSON object only.

Screenshot {index} of {total}.
OCR labels visible in the image: {labels}
Previous step titles: {previous}

Rules:
- title: one short imperative sentence, under 60 characters.
- body: one or two sentences. Say what the person does and what happens.
- callout: copy one exact OCR label that should be highlighted. Use an empty string if none fits.
- Do not invent buttons or menu items that are not in the OCR labels.
- confidence: 0.0 to 1.0.

JSON shape:
{{"title": "...", "body": "...", "callout": "...", "confidence": 0.0}}
"""


def parse_reply(text: str) -> dict[str, object] | None:
    value = text.strip()
    start, end = value.find("{"), value.rfind("}")
    if start >= 0 and end > start:
        value = value[start : end + 1]
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


class QwenWriter:
    name = "qwen3-vl-2b-4bit"

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or model_dir()
        self._model = None
        self._processor = None
        self._generate = None
        self._template = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if not (self.path / "model.safetensors").exists():
            raise RuntimeError(
                f"model not found at {self.path}. Run: python scripts/download_model.py"
            )
        try:
            from mlx_vlm import generate, load
            from mlx_vlm.prompt_utils import apply_chat_template
        except ImportError as exc:
            raise RuntimeError(
                "MLX is not installed. Install with: uv pip install -e '.[model]'"
            ) from exc
        self._generate = generate
        self._template = apply_chat_template
        self._model, self._processor = load(str(self.path))

    def write(self, index, total, image, lines, previous) -> StepDraft:
        self._load()
        assert self._model is not None and self._processor is not None
        labels = " | ".join(line.text for line in lines[:18]) or "none"
        prompt = PROMPT.format(
            index=index + 1,
            total=total,
            labels=labels,
            previous="; ".join(previous[-3:]) or "none",
        )
        image = image.convert("RGB")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
            temp = Path(handle.name)
        try:
            image.save(temp)
            text = self._template(
                self._processor, self._model.config, prompt, num_images=1
            )
            result = self._generate(
                self._model,
                self._processor,
                text,
                str(temp),
                max_tokens=180,
                verbose=False,
            )
        finally:
            temp.unlink(missing_ok=True)
        data = parse_reply(str(result.text))
        if not data:
            fallback = HeuristicWriter().write(index, total, image, lines, previous)
            return StepDraft(
                title=fallback.title,
                body=fallback.body,
                callout=fallback.callout,
                confidence=0.2,
            )
        title = re.sub(r"\s+", " ", str(data.get("title") or "")).strip()[:70]
        body = re.sub(r"\s+", " ", str(data.get("body") or "")).strip()[:280]
        return StepDraft(
            title=title or f"Step {index + 1}",
            body=body or "Review this screen before continuing.",
            callout=str(data.get("callout") or "").strip(),
            confidence=max(0.0, min(1.0, float(data.get("confidence") or 0.0))),
        )


def build_writer(name: str = "auto") -> StepWriter:
    name = (name or "auto").lower()
    if name in {"heuristic", "none"}:
        return HeuristicWriter()
    if name in {"auto", "qwen", "mlx"}:
        if (model_dir() / "model.safetensors").exists():
            return QwenWriter()
        if name == "auto":
            return HeuristicWriter()
        raise RuntimeError("Qwen model not found. Run: python scripts/download_model.py")
    raise ValueError(f"unknown writer: {name}")
