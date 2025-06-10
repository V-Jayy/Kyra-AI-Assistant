import os
import subprocess
import webbrowser
from typing import Dict, Tuple


def open_website(url: str) -> Tuple[bool, str]:
    """Open a website in the default browser."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open_new_tab(url)
        return True, f"Opening {url}"
    except Exception as exc:
        return False, str(exc)


def launch(app_path: str) -> Tuple[bool, str]:
    """Launch an application given its path."""
    try:
        os.startfile(app_path)  # type: ignore[attr-defined]
        return True, f"Launching {app_path}"
    except Exception as exc:
        try:
            subprocess.Popen(app_path)
            return True, f"Launching {app_path}"
        except Exception:
            return False, str(exc)


def search_files(pattern: str, root: str) -> Tuple[bool, str]:
    """Search for files matching pattern under root."""
    matches = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if pattern.lower() in f.lower():
                matches.append(os.path.join(dirpath, f))
    if matches:
        return True, "Found: " + "; ".join(matches[:5])
    return False, "No files found"


def reveal_folder(path: str) -> Tuple[bool, str]:
    """Open folder in Explorer."""
    try:
        os.startfile(path)  # type: ignore[attr-defined]
        return True, f"Opening folder {path}"
    except Exception as exc:
        return False, str(exc)


# Dispatcher mapping
actions: Dict[str, callable] = {
    "open_website": open_website,
    "launch": launch,
    "search_files": search_files,
    "reveal_folder": reveal_folder,
}


def dispatch(action_name: str, **kwargs) -> Tuple[bool, str]:
    if action_name not in actions:
        return False, f"Unknown action {action_name}"
    return actions[action_name](**kwargs)
