from __future__ import annotations

import inspect
import functools
import fnmatch
from typing import Callable, Dict, Tuple, Any, List
import re
import urllib.parse

from .utils import derive_glob_from_phrase

__all__ = [
    "open_website",
    "sanitize_domain",
    "launch_app",
    "search_files",
    "play_music",
    "list_tools",
    "get_openai_tools",
    "validate_tool_args",
    "derive_glob_from_phrase",
]

_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Tool schemas used for OpenAI function calling
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "open_website",
        "parameters": {"type": "object", "required": ["url"]},
    },
    {
        "name": "launch_app",
        "parameters": {"type": "object", "required": ["app"]},
    },
    {
        "name": "open_explorer",
        "parameters": {"type": "object", "required": ["path"]},
    },
    {
        "name": "find_file_and_open",
        "parameters": {"type": "object", "required": []},
    },
    {
        "name": "search_files",
        "parameters": {"type": "object", "required": ["directory", "pattern"]},
    },
    {
        "name": "play_music",
        "parameters": {"type": "object", "required": ["song"]},
    },
]

_TOOL_SCHEMA_MAP = {s["name"]: s["parameters"] for s in TOOL_SCHEMAS}


def tool(fn: Callable[..., Tuple[bool, str]]) -> Callable[..., Tuple[bool, str]]:
    """Register a function as an assistant tool."""
    _REGISTRY[fn.__name__] = {
        "signature": str(inspect.signature(fn)),
        "doc": inspect.getdoc(fn) or "",
        "callable": fn,
    }

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[bool, str]:
        return fn(*args, **kwargs)

    return wrapper


def list_tools() -> Dict[str, Dict[str, str]]:
    return {
        k: {"signature": v["signature"], "doc": v["doc"]} for k, v in _REGISTRY.items()
    }


def get_openai_tools() -> List[Dict[str, Any]]:
    """Return tool metadata formatted for OpenAI function-calling."""
    tools: List[Dict[str, Any]] = []
    for name, meta in _REGISTRY.items():
        params = _TOOL_SCHEMA_MAP.get(name, {"type": "object", "properties": {}})
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": meta["doc"],
                    "parameters": params,
                },
            }
        )
    return tools


def validate_tool_args(name: str, args: Dict[str, Any]) -> None:
    """Validate arguments for a registered tool using JSON schema."""
    schema = _TOOL_SCHEMA_MAP.get(name)
    if not schema:
        return
    from jsonschema import validate

    validate(args, schema)


import os
import subprocess
import webbrowser


def sanitize_domain(text: str) -> str:
    """Return a clean domain or empty string if *text* is not valid."""
    text = text.strip().lower()
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"^www\.", "", text)
    text = text.split()[0]
    text = text.split("/")[0]
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", text):
        return text
    return ""


@tool
def open_website(url: str) -> Tuple[bool, str]:
    """Open a website in the default browser."""
    clean = sanitize_domain(url)
    if clean:
        full_url = "https://" + clean if not clean.startswith("http") else clean
    else:
        query = urllib.parse.quote(url.strip())
        full_url = f"https://www.google.com/search?q={query}"
    try:
        webbrowser.open_new_tab(full_url)
        action = "Opening" if clean else "Searching for"
        return True, f"{action} {full_url}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def play_music(song: str) -> Tuple[bool, str]:
    """Open YouTube search results for the given *song*."""
    query = urllib.parse.quote(song)
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        webbrowser.open(url)
        return True, f"Playing {song}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def launch_app(*, app: str | None = None, program: str | None = None, path: str | None = None) -> Tuple[bool, str]:
    """Launch an application."""
    target = program or app or path
    if not target:
        return False, "No program specified"
    try:
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen([target])
        return True, f"Launching {target}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def search_files(directory: str, pattern: str, **_unused: Any) -> Tuple[bool, str]:
    """Search for files under a directory."""
    root = os.path.expanduser(directory)
    glob_pattern = derive_glob_from_phrase(pattern)
    matches: List[str] = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if fnmatch.fnmatch(f.lower(), glob_pattern.lower()):
                matches.append(os.path.join(dirpath, f))
    if matches:
        return True, "; ".join(matches[:5])
    return False, "No files found"
