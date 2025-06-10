from __future__ import annotations

from typing import Dict

_EXTENSION_MAP: Dict[str, str] = {
    "text": "*.txt",
    "txt": "*.txt",
    "pdf": "*.pdf",
    "python": "*.py",
    "png": "*.png",
    "jpg": "*.jpg",
    "jpeg": "*.jpeg",
    "image": "*.png",
}


def derive_glob_from_phrase(phrase: str) -> str:
    """Best-effort conversion from a phrase to a glob pattern."""
    words = phrase.lower().split()
    for w in words:
        if w in _EXTENSION_MAP:
            return _EXTENSION_MAP[w]
    return "*" + "*".join(words) + "*"
