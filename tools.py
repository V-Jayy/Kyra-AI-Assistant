from __future__ import annotations

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Callable


def open_website(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open_new_tab(url)
    return f"Opening {url}"


def launch_program(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(path)
    try:
        os.startfile(str(p))  # type: ignore[attr-defined]
    except Exception:
        subprocess.Popen([str(p)])
    return f"Launching {p}"


def search_files(query: str) -> str:
    root = Path.home()
    matches = [str(p) for p in root.rglob(f"*{query}*")][:5]
    if not matches:
        return "No files found"
    return "Found: " + "; ".join(matches)


def open_explorer(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(path)
    try:
        os.startfile(str(p))  # type: ignore[attr-defined]
    except Exception:
        subprocess.Popen(["xdg-open", str(p)])
    return f"Opening {p}"


def lock_pc() -> str:
    if os.name == "nt":
        subprocess.call(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif sys.platform == "darwin":
        subprocess.call(["osascript", "-e", 'tell application "System Events" to keystroke "q" using {control down, command down}'])
    else:
        subprocess.call(["gnome-screensaver-command", "--lock"])
    return "Locking workstation"


def volume_up() -> str:
    if os.name == "nt":
        subprocess.call(["nircmd.exe", "changesysvolume", "2000"])
    else:
        subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
    return "Volume up"


def volume_down() -> str:
    if os.name == "nt":
        subprocess.call(["nircmd.exe", "changesysvolume", "-2000"])
    else:
        subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
    return "Volume down"


ALL_TOOLS: Dict[str, Callable[..., str]] = {
    "open_website": open_website,
    "launch_program": launch_program,
    "search_files": search_files,
    "open_explorer": open_explorer,
    "lock_pc": lock_pc,
    "volume_up": volume_up,
    "volume_down": volume_down,
}
