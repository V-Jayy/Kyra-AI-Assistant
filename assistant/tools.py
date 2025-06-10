import inspect
import json
import functools

_REGISTRY = {}

def tool(fn):
    """Decorator registering a callable as an assistant tool."""
    _REGISTRY[fn.__name__] = {
        "sig": str(inspect.signature(fn)),
        "doc": inspect.getdoc(fn) or "",
        "callable": fn,
    }
    # Return the original function so object identity is preserved for tests
    return fn


def export_capabilities(path="capabilities.json"):
    """Write the registry to a JSON file for introspection."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({k: {"sig": v["sig"], "doc": v["doc"]} for k, v in _REGISTRY.items()}, f, indent=2)
