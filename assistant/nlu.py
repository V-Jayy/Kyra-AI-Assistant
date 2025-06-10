import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from rapidfuzz.fuzz import token_set_ratio

# path to filler words file used for basic text normalisation
FILLER_FILE = Path(__file__).with_name("filler_words.txt")


def normalize(text: str) -> str:
    """Lowercase, remove punctuation and filler words."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    if FILLER_FILE.exists():
        with open(FILLER_FILE, "r", encoding="utf-8") as f:
            fillers = [re.escape(w.strip()) for w in f if w.strip()]
        if fillers:
            pattern = re.compile(r"\b(?:" + "|".join(fillers) + r")\b", re.I)
            text = pattern.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class Intent:
    id: str
    patterns: List[re.Pattern]
    canonical: str
    synonyms: List[str]
    extractor: Callable[[re.Match], Dict[str, str]]


INTENTS: List[Intent] = []


def _register_intents() -> None:
    def site_extract(m: re.Match) -> Dict[str, str]:
        site = m.group("site").strip().lower()
        site = re.sub(r"^the\s+", "", site)
        if not re.search(r"\.[a-z]{2,}$", site):
            site += ".com"
        return {"url": site}

    INTENTS.append(
        Intent(
            id="open_website",
            patterns=[
                re.compile(r"(?:open|go to|pull up|visit)\s+(?:the\s+)?(?P<site>[\w\.-]+)", re.I)
            ],
            canonical="open website",
            synonyms=["go to site", "pull up site"],
            extractor=site_extract,
        )
    )

    def app_extract(m: re.Match) -> Dict[str, str]:
        name = m.group("app").strip().lower()
        mapping = {
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "discord": "discord.exe",
            "notepad": "notepad.exe",
        }
        path = mapping.get(name, name)
        return {"path": path}

    INTENTS.append(
        Intent(
            id="launch_app",
            patterns=[re.compile(r"(?:open|launch|start)\s+(?P<app>[\w\s]+)", re.I)],
            canonical="launch app",
            synonyms=["open app", "start app"],
            extractor=app_extract,
        )
    )

    def search_extract(m: re.Match) -> Dict[str, str]:
        query = m.group("query").strip()
        return {"query": query}

    INTENTS.append(
        Intent(
            id="search_files",
            patterns=[re.compile(r"(?:find file|search for)\s+(?P<query>.+)", re.I)],
            canonical="search files",
            synonyms=["find file", "search for file"],
            extractor=search_extract,
        )
    )

    def folder_extract(m: re.Match) -> Dict[str, str]:
        folder = m.group("folder").lower()
        mapping = {"downloads": os.path.expandvars("%USERPROFILE%/Downloads")}
        path = mapping.get(folder, folder)
        return {"path": path}

    INTENTS.append(
        Intent(
            id="reveal_folder",
            patterns=[re.compile(r"(?:open|show)(?: my)? (?P<folder>downloads)(?: folder)?", re.I)],
            canonical="open downloads folder",
            synonyms=["show my downloads folder", "open downloads"],
            extractor=folder_extract,
        )
    )


_register_intents()


def classify(text: str) -> Tuple[str, Dict[str, str], float]:
    norm = normalize(text)

    # pass 1: regex patterns
    for intent in INTENTS:
        for pat in intent.patterns:
            m = pat.search(norm)
            if m:
                args = intent.extractor(m)
                return intent.id, args, 1.0

    # pass 2: fuzzy similarity
    best_intent = None
    best_score = 0
    for intent in INTENTS:
        for phrase in [intent.canonical] + intent.synonyms:
            score = token_set_ratio(norm, phrase)
            if score > best_score:
                best_score = score
                best_intent = intent

    confidence = best_score / 100.0
    if best_intent is None:
        return "chat", {}, 0.0
    return best_intent.id, {}, confidence
