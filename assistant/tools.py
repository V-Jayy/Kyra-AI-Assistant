"""Tool registry utilities and simple text matcher."""

from dataclasses import dataclass
from typing import Callable, Pattern, Dict, Any, List, Tuple, Optional
import inspect
import json
import functools
import re

_REGISTRY: Dict[str, Dict[str, Any]] = {}


def tool(fn: Callable) -> Callable:
    """Decorator registering a callable as an assistant tool."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    _REGISTRY[fn.__name__] = {
        "sig": str(inspect.signature(fn)),
        "doc": inspect.getdoc(fn) or "",
        "callable": wrapper,
    }

    return wrapper


@dataclass
class Tool:
    name: str
    description: str
    trigger_patterns: List[Pattern]
    handler: Callable[[Dict[str, Any]], Tuple[bool, str]]


TOOL_REGISTRY: List[Tool] = []


def register_tool(tool: Tool) -> None:
    """Add a Tool object to the registry."""
    TOOL_REGISTRY.append(tool)


def match_tool(cmd: str) -> Tuple[Optional[Tool], Dict[str, str]]:
    """Return the first matching Tool and extracted parameters."""
    for tool in TOOL_REGISTRY:
        for pat in tool.trigger_patterns:
            m = pat.search(cmd)
            if m:
                return tool, m.groupdict()
    return None, {}


def export_capabilities(path="capabilities.json"):
    """Write the registry to a JSON file for introspection."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({k: {"sig": v["sig"], "doc": v["doc"]} for k, v in _REGISTRY.items()}, f, indent=2)
