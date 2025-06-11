from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import re

from rapidfuzz import fuzz


@dataclass
class Action:
    name: str
    args: Dict[str, str]


_PATTERNS = {
    "open_explorer": (
        re.compile(r"(?:open|show) (?P<path>(?:[A-Za-z]:|~|/).+|.+(?:folder|directory).*)", re.I),
        "path",
    ),
    "create_note": (re.compile(r"(?:note|remember) (?P<content>.+)", re.I), "content"),
    "open_website": (re.compile(r"(?:open|visit|go to) (?P<url>.+)", re.I), "url"),
    "launch_app": (re.compile(r"(?:launch|open|start) (?P<exe>.+)", re.I), "app"),
    "play_song": (re.compile(r"(?:play|listen to) (?P<song>.+)", re.I), "query"),
    "download_app": (re.compile(r"(?:download|install) (?P<pkg>.+)", re.I), "package"),
    "kill_process": (re.compile(r"(?:kill|close|terminate) (?P<proc>.+)", re.I), "name"),
}

_CHOICES = {
    "open_explorer": "open folder",
    "create_note": "create note",
    "open_website": "open website",
    "launch_app": "launch app",
    "play_song": "play song",
    "download_app": "download app",
    "kill_process": "kill process",
}


def fuzzy_match(cmd: str) -> Optional[Action]:
    text = cmd.lower().strip()
    for name, (regex, arg_key) in _PATTERNS.items():
        m = regex.search(text)
        if m:
            return Action(name, {arg_key: m.group(1).strip()})

    scores = {
        name: fuzz.partial_ratio(text, phrase)
        for name, phrase in _CHOICES.items()
    }
    best_name = max(scores, key=scores.get)
    score = scores[best_name]
    if score >= 80:
        _, key = _PATTERNS[best_name]
        arg = text.replace(_CHOICES[best_name], "", 1).strip()
        if not arg:
            arg = text
        return Action(best_name, {key: arg})
    if score >= 60:
        return Action("repeat", {})
    return None
