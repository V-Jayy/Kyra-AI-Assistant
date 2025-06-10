from typing import Any, Callable, Dict, Tuple

from . import actions
from .nlu import classify
from .tools import _REGISTRY


class Router:
    """Route user text to an action function based on NLU classification."""

    def select(self, text: str) -> Tuple[Callable[..., Tuple[bool, str]] | None, Dict[str, Any], str, float]:
        intent, args, conf = classify(text)
        fn = None
        if intent != "chat" and conf >= 0.75:
            fn = _REGISTRY.get(intent, {}).get("callable")
        return fn, args, intent, conf
