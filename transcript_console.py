import threading
import time
import curses
import config


class TranscriptConsole:
    """Simple curses-based transcript window."""

    def __init__(self) -> None:
        self.enabled = bool(config.DEBUG)
        self.lines: list[tuple[str, str]] = []
        if not self.enabled:
            return
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def log(self, speaker: str, text: str) -> None:
        if not self.enabled:
            return
        with self.lock:
            ts = time.strftime("%H:%M:%S")
            self.lines.append((f"[{ts}] {speaker}: ", text))
            if len(self.lines) > 50:
                self.lines = self.lines[-50:]

    def _run(self) -> None:
        stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        while True:
            with self.lock:
                stdscr.erase()
                h, _ = stdscr.getmaxyx()
                start = max(len(self.lines) - h, 0)
                for idx, (prefix, msg) in enumerate(self.lines[start:]):
                    color = 1 if prefix.strip().startswith("USER") else 2
                    if prefix.strip().startswith("ERROR"):
                        color = 3
                    stdscr.addstr(idx, 0, prefix + msg, curses.color_pair(color))
                stdscr.refresh()
            time.sleep(0.5)


class NoopConsole:
    def log(self, *_: str) -> None:  # pragma: no cover - simple noop
        pass


def get_console() -> TranscriptConsole:
    """Factory respecting config.DEBUG."""
    if config.DEBUG:
        return TranscriptConsole()
    return NoopConsole()  # type: ignore

if __name__ == "__main__":
    from assistant import main
    main()
