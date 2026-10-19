"""Colori ANSI minimali. Disattivati se l'output non e' un terminale o con NO_COLOR."""

import os
import re
import sys

CODES = {
    "bold": "1", "dim": "2", "underline": "4", "reverse": "7",
    "red": "31", "green": "32", "yellow": "33", "blue": "34",
    "magenta": "35", "cyan": "36", "white": "97", "gray": "90",
}


def enabled(stream=None) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return (stream or sys.stdout).isatty()


def paint(text: str, *styles: str, stream=None) -> str:
    if not styles or not enabled(stream):
        return str(text)
    seq = ";".join(CODES[s] for s in styles)
    return f"\033[{seq}m{text}\033[0m"


def highlight(text: str, terms: list[str], *base: str, regex: bool = False) -> str:
    """Evidenzia le occorrenze di `terms` in `text` (case-insensitive)."""
    if not terms or not enabled():
        return text
    pattern = "|".join(t if regex else re.escape(t) for t in terms)
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return text
    reset = "\033[0m" + (f"\033[{';'.join(CODES[s] for s in base)}m" if base else "")
    return rx.sub(lambda m: f"\033[1;30;43m{m.group(0)}{reset}", text)


def error(msg: str) -> None:
    print(f"{paint('✗', 'red', 'bold', stream=sys.stderr)} {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"{paint('✓', 'green', 'bold')} {msg}")


def warn(msg: str) -> None:
    print(f"{paint('!', 'yellow', 'bold')} {msg}")


def info(msg: str) -> None:
    print(paint(msg, "dim"))
