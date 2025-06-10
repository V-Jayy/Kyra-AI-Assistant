from __future__ import annotations


class Transcript:
    def __init__(self, enable: bool) -> None:
        self.enable = enable
        try:
            from colorama import Fore, Style

            self.colors = {
                "USER": Fore.CYAN,
                "BOT": Fore.GREEN,
                "ERR": Fore.RED,
            }
            self.reset = Style.RESET_ALL
        except Exception:  # pragma: no cover - colorama optional
            self.colors = {k: "" for k in ["USER", "BOT", "ERR"]}
            self.reset = ""

    def log(self, tag: str, msg: str) -> None:
        if not self.enable:
            return
        color = self.colors.get(tag, "")
        print(f"[{tag}] {color}{msg}{self.reset}")
