import os
import subprocess
import webbrowser
from typing import Dict, Tuple

from .tools import (
    tool,
    export_capabilities,
    Tool,
    register_tool,
)
import re


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


register_tool(
    Tool(
        name="open_website",
        description="Opens a website in the default browser",
        trigger_patterns=[
            re.compile(r"(?:open|launch|go to)\s+(?P<url>https?://\S+)", re.I),
            re.compile(r"(?:open|launch|go to)(?:\s+the)?\s+(?:website\s+)?(?P<url>[\w.-]+\.[a-z]{2,})", re.I),
            re.compile(r"(?:open|launch|go to)\s+(?P<url>\w+) dot com", re.I),
            re.compile(r"open\s+(?P<url>youtube(?:\.com)?)", re.I),
            re.compile(r"open\s+(?P<url>reddit(?:\.com)?)", re.I),
        ],
        handler=lambda params: open_website(params.get("url", "")),
    )
)


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


register_tool(
    Tool(
        name="launch_app",
        description="Launch an application given its path",
        trigger_patterns=[
            re.compile(r"(?:launch|start|open)\s+(?P<path>\w+)$", re.I),
            re.compile(r"open application (?P<path>\w+)", re.I),
        ],
        handler=lambda params: launch_app(params.get("path", "")),
    )
)


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


register_tool(
    Tool(
        name="search_files",
        description="Search for files matching pattern under root",
        trigger_patterns=[
            re.compile(r"search for (?P<pattern>.+) in (?P<root>.+)", re.I),
            re.compile(r"find (?P<pattern>.+) in (?P<root>.+)", re.I),
            re.compile(r"look for (?P<pattern>.+) in (?P<root>.+)", re.I),
        ],
        handler=lambda params: search_files(
            params.get("pattern", ""), params.get("root", "~")
        ),
    )
)


@tool
def reveal_folder(path: str) -> Tuple[bool, str]:
    """Open folder in Explorer."""
    try:
        os.startfile(path)  # type: ignore[attr-defined]
        return True, f"Opening folder {path}"
    except Exception as exc:
        return False, str(exc)


register_tool(
    Tool(
        name="reveal_folder",
        description="Open folder in Explorer",
        trigger_patterns=[
            re.compile(r"(?:open|show|reveal)\s+(?P<path>.+) (?:folder|directory)", re.I),
            re.compile(r"show (?:me )?my (?P<path>downloads|documents|pictures|music)", re.I),
        ],
        handler=lambda params: reveal_folder(params.get("path", "")),
    )
)

# Export tool registry to capabilities.json when this module is imported
export_capabilities()
