from __future__ import annotations

import inspect
import functools
import fnmatch
from typing import Callable, Dict, Tuple, Any, List

import os
import subprocess
import webbrowser


from .utils import derive_glob_from_phrase

__all__ = [
    "open_website",
    "launch_app",
    "search_files",
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
        "parameters": {
            "type": "object",
            "required": ["directory", "pattern"],
        },
    },
]

_TOOL_SCHEMA_MAP = {s["name"]: s["parameters"] for s in TOOL_SCHEMAS}


def tool(
    fn: Callable[..., Tuple[bool, str]]
) -> Callable[..., Tuple[bool, str]]:
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
        k: {"signature": v["signature"], "doc": v["doc"]}
        for k, v in _REGISTRY.items()
    }


def get_openai_tools() -> List[Dict[str, Any]]:
    """Return tool metadata formatted for OpenAI function-calling."""
    tools: List[Dict[str, Any]] = []
    for name, meta in _REGISTRY.items():
        params = _TOOL_SCHEMA_MAP.get(
            name, {"type": "object", "properties": {}}
        )
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


@tool
def open_website(url: str) -> Tuple[bool, str]:
    """Open a website in the default browser."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open_new_tab(url)
        return True, f"Opening {url}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def launch_app(app: str) -> Tuple[bool, str]:
    """Launch an application."""
    path = app
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen([path])
        return True, f"Launching {path}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def search_files(
    directory: str,
    pattern: str,
    **_unused: Any,
) -> Tuple[bool, str]:
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
