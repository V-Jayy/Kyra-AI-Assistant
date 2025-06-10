import os
import subprocess
import webbrowser
from typing import Dict, Tuple

from .tools import tool, export_capabilities


@tool
def open_website(url: str) -> Tuple[bool, str]:
    """Open a website in the default browser."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open_new_tab(url)
        return True, f"Opening {url}"
    except Exception as exc:
        return False, str(exc)


@tool
def launch_app(path: str) -> Tuple[bool, str]:
    """Launch an application given its path."""
    try:
        os.startfile(path)  # type: ignore[attr-defined]
        return True, f"Launching {path}"
    except Exception as exc:
        try:
            subprocess.Popen(path)
            return True, f"Launching {path}"
        except Exception:
            return False, str(exc)


@tool
def search_files(pattern: str, root: str = "~") -> Tuple[bool, str]:
    """Search for files matching pattern under root."""
    matches = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if pattern.lower() in f.lower():
                matches.append(os.path.join(dirpath, f))
    if matches:
        return True, "Found: " + "; ".join(matches[:5])
    return False, "No files found"


@tool
def reveal_folder(path: str) -> Tuple[bool, str]:
    """Open folder in Explorer."""
    try:
        os.startfile(path)  # type: ignore[attr-defined]
        return True, f"Opening folder {path}"
    except Exception as exc:
        return False, str(exc)

# Export tool registry to capabilities.json when this module is imported
export_capabilities()
