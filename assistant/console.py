from datetime import datetime
from pathlib import Path

class TranscriptConsole:
    """Simple live transcript console using Rich if available."""

    def __init__(self, debug: bool = True):
        self.debug = debug
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"{datetime.now():%Y-%m-%d}.log"
        try:
            from rich.console import Console
            self.console = Console()
        except Exception:  # pragma: no cover - rich optional
            self.console = None

    def log(self, message: str, user: bool = True) -> None:
        if not self.debug:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        tag = "USER" if user else "ASSIST"
        line = f"[{ts}] {tag}: {message}"
        if self.console:
            style = "bold green" if user else "cyan"
            self.console.print(line, style=style)
        else:
            print(line)
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
