"""Small, dependency-free PII patterns for screenshot redaction."""

from __future__ import annotations

import re

from .ocr import TextLine

EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
CARD = re.compile(r"(?<!\d)(?:\d[ \-]?){13,19}(?!\d)")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()\-]{5,}\d)(?!\d)")


def luhn(value: str) -> bool:
    digits = [int(ch) for ch in re.sub(r"\D", "", value)]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def is_sensitive(text: str) -> bool:
    if EMAIL.search(text) or SSN.search(text) or IBAN.search(text):
        return True
    for match in CARD.finditer(text):
        if luhn(match.group(0)):
            return True
    for match in PHONE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if 7 <= len(digits) <= 15:
            return True
    return False


def masks_for(lines: list[TextLine]) -> list[tuple[float, float, float, float]]:
    return [line.bbox for line in lines if is_sensitive(line.text)]
