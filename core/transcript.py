from __future__ import annotations

import os
from rich.console import Console
from rich.text import Text


class Transcript:
    def __init__(self, enable: bool) -> None:
        self.enable = enable
        self.console = Console()
        self.file = "transcript.txt"

    def _append(self, line: str) -> None:
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        if os.path.getsize(self.file) > 1_000_000:
            with open(self.file, "rb") as f:
                f.seek(-1_000_000, os.SEEK_END)
                data = f.read()
            with open(self.file, "wb") as f:
                f.write(data)

    def log(self, tag: str, msg: str) -> None:
        if not self.enable:
            return
        colors = {
            "PART": "grey50",
            "USER": "cyan",
            "BOT": "green",
            "SAY": "magenta",
            "ERR": "red",
        }
        style = colors.get(tag, "white")
        self.console.print(Text(f"[{tag}] {msg}", style=style))
        self._append(f"[{tag}] {msg}")
