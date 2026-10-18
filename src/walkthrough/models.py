"""Guide data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Step:
    number: int
    image: str
    title: str
    body: str
    callout: str = ""
    bbox: tuple[float, float, float, float] | None = None
    image_size: tuple[int, int] | None = None
    confidence: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "number": self.number,
            "image": self.image,
            "title": self.title,
            "body": self.body,
            "callout": self.callout,
            "bbox": list(self.bbox) if self.bbox else None,
            "image_size": list(self.image_size) if self.image_size else None,
            "confidence": round(self.confidence, 3),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Step:
        bbox = data.get("bbox")
        size = data.get("image_size")
        return cls(
            number=int(data.get("number") or 0),
            image=str(data.get("image") or ""),
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            callout=str(data.get("callout") or ""),
            bbox=tuple(float(value) for value in bbox) if bbox else None,
            image_size=tuple(int(value) for value in size) if size else None,
            confidence=float(data.get("confidence") or 0.0),
        )


@dataclass(slots=True)
class Guide:
    title: str
    summary: str
    steps: list[Step] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "summary": self.summary,
            "steps": [step.to_dict() for step in self.steps],
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Guide:
        return cls(
            title=str(data.get("title") or ""),
            summary=str(data.get("summary") or ""),
            steps=[Step.from_dict(item) for item in data.get("steps", [])],
            warnings=[str(item) for item in data.get("warnings", [])],
        )
