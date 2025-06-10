from __future__ import annotations

import inspect
import functools
from typing import Callable, Dict, Tuple, Any

_REGISTRY: Dict[str, Dict[str, Any]] = {}


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


import os
import subprocess
import webbrowser


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
def launch_app(path: str) -> Tuple[bool, str]:
    """Launch an application."""
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen([path])
        return True, f"Launching {path}"
    except Exception as exc:  # pragma: no cover - platform dependent
        return False, str(exc)


@tool
def search_files(pattern: str, root: str = "~") -> Tuple[bool, str]:
    """Search for files under a directory."""
    root = os.path.expanduser(root)
    matches = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if pattern.lower() in f.lower():
                matches.append(os.path.join(dirpath, f))
    if matches:
        return True, "; ".join(matches[:5])
    return False, "No files found"
