from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Dict, Tuple, Optional

from rapidfuzz import fuzz

from .tools import sanitize_domain

logger = logging.getLogger(__name__)

FILLER_RE = re.compile(r"\b(?:please|can you|could you|would you|i want to|i wanna|i want|\s+)\b", re.I)


def _clean(text: str) -> str:
    text = text.lower().strip()
    text = FILLER_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text)


def match_intent(text: str) -> Tuple[Optional[str], Dict[str, str]]:
    """Return tool name and arguments if recognised."""
    cleaned = _clean(text)

    m = re.search(r"(?:play|listen to|hear) (?P<song>.+)", cleaned)
    if m:
        song = re.sub(r" on youtube$", "", m.group("song"), flags=re.I).strip()
        logger.debug(
            "Mapped input '%s' to play_music with arg: '%s'", text, song
        )
        return "play_music", {"url": None, "query": song}

    m = re.search(r"(?:search for|look up) (?P<query>.+)", cleaned)
    if m:
        q = m.group("query").strip()
        url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
        logger.debug("Mapped input '%s' to open_website search with arg: '%s'", text, q)
        return "open_website", {"url": url}

    m = re.search(r"(?:open|visit|go to) (?P<site>.+)", cleaned)
    if m:
        site = m.group("site").strip()
        logger.debug("Mapped input '%s' to open_website with arg: '%s'", text, site)
        return "open_website", {"url": site}

    # Similarity fallback for one-word commands
    scores = {
        "open_website": fuzz.partial_ratio(cleaned, "open"),
        "play_music": fuzz.partial_ratio(cleaned, "play"),
        "open_search": fuzz.partial_ratio(cleaned, "search"),
    }
    best = max(scores, key=scores.get)
    if scores[best] > 60:
        if best == "open_search":
            url = f"https://www.google.com/search?q={urllib.parse.quote(cleaned)}"
            return "open_website", {"url": url}
        elif best == "open_website":
            dom = sanitize_domain(cleaned)
            arg = dom if dom else cleaned
            return "open_website", {"url": arg}
        else:
            return "play_music", {"url": None, "query": cleaned}

    return None, {}

