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
    "kill_process",
    "search_files",
    "play_music",
    "install_cmd",
    "uninstall_cmd",
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
        "name": "kill_process",
        "parameters": {"type": "object", "required": ["name"]},
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
    {
        "name": "install_cmd",
        "parameters": {"type": "object", "required": []},
    },
    {
        "name": "uninstall_cmd",
        "parameters": {"type": "object", "required": []},
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
import platform
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


@tool
def kill_process(name: str) -> Tuple[bool, str]:
    """Force terminate processes matching *name*."""
    proc = name.lower().replace(".exe", "")
    try:
        if platform.system() == "Windows":
            subprocess.run([
                "taskkill",
                "/F",
                "/IM",
                f"{proc}.exe",
            ], check=True)
        else:
            subprocess.run(["pkill", "-f", proc], check=True)
        return True, f"Killed {proc}"
    except subprocess.CalledProcessError:
        return False, f"Could not kill {proc}"


@tool
def install_cmd() -> Tuple[bool, str]:
    """Install Kyra system-wide with a `Kyra` command."""
    import shutil
    import sys
    import subprocess

    if os.name == "nt":
        target = os.environ.get("KYRA_INSTALL_DIR", r"C:\\Program Files\\Kyra")
        launcher = os.environ.get("KYRA_LAUNCHER_PATH", r"C:\\Windows\\Kyra.bat")
        try:
            os.makedirs(target, exist_ok=True)
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            shutil.copytree(root, target, dirs_exist_ok=True)
            venv_dir = os.path.join(target, "venv")
            if not os.path.isdir(venv_dir):
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
                pip = os.path.join(venv_dir, "Scripts", "pip.exe")
                req = os.path.join(target, "requirements.txt")
                subprocess.check_call([pip, "install", "-r", req])

            os.makedirs(os.path.dirname(launcher), exist_ok=True)
            with open(launcher, "w", newline="") as f:
                f.write("@echo off\n")
                f.write(f'cd /d "{target}"\n')
                f.write(f'"{os.path.join(venv_dir, "Scripts", "python.exe")}" -m app.assistant %*\n')
            return True, f"Installed to {target}"
        except Exception as exc:  # pragma: no cover - platform dependent
            return False, str(exc)

    # Non-Windows fallback: copy to first writable PATH dir
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for p in os.getenv("PATH", "").split(os.pathsep):
        if not p or not os.access(p, os.W_OK):
            continue
        try:
            dest = os.path.join(p, "Kyra")
            shutil.copytree(root, dest, dirs_exist_ok=True)
            script = os.path.join(p, "Kyra")
            content = (
                "#!/bin/sh\n"
                f'cd "{dest}"\n'
                f'exec {sys.executable} -m app.assistant "$@"\n'
            )
            with open(script, "w", newline="") as f:
                f.write(content)
            os.chmod(script, 0o755)
            return True, f"Installed to {p}"
        except Exception:
            continue
    return False, "No writable directory in PATH"


@tool
def uninstall_cmd() -> Tuple[bool, str]:
    """Remove the files installed by :func:`install_cmd`."""
    import shutil

    if os.name == "nt":
        target = os.environ.get("KYRA_INSTALL_DIR", r"C:\\Program Files\\Kyra")
        launcher = os.environ.get("KYRA_LAUNCHER_PATH", r"C:\\Windows\\Kyra.bat")
        try:
            shutil.rmtree(target, ignore_errors=True)
            if os.path.exists(launcher):
                os.remove(launcher)
            return True, "Uninstalled"
        except Exception as exc:  # pragma: no cover - platform dependent
            return False, str(exc)

    success = False
    for p in os.getenv("PATH", "").split(os.pathsep):
        if not p:
            continue
        try:
            target_dir = os.path.join(p, "Kyra")
            if os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
                success = True
            script = os.path.join(p, "Kyra")
            if os.path.exists(script):
                os.remove(script)
                success = True
        except Exception:
            continue
    if success:
        return True, "Uninstalled"
    return False, "Nothing removed"
