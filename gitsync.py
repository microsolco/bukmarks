"""Versionamento automatico con git: commit e push senza intervento dell'utente."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .store import FILE_NAME, BukmarksError


@dataclass
class SaveResult:
    commit: str | None = None   # hash breve, None se non c'erano modifiche
    pushed: bool | None = None  # None = nessun remote configurato
    error: str | None = None    # motivo del push fallito


def git(home: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=home, capture_output=True, text=True, timeout=120
        )
    except FileNotFoundError as e:
        raise BukmarksError("git non trovato nel PATH") from e
    except subprocess.TimeoutExpired as e:
        raise BukmarksError(f"git {args[0]}: timeout") from e
    if check and proc.returncode != 0:
        raise BukmarksError(f"git {args[0]}: {(proc.stderr or proc.stdout).strip()}")
    return proc


def ensure_repo(home: Path) -> None:
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not (home / ".git").exists():
        git(home, "init", "-q", "-b", "main")


def remote_url(home: Path) -> str | None:
    out = git(home, "remote", "get-url", "origin", check=False)
    return out.stdout.strip() if out.returncode == 0 else None


def set_remote(home: Path, url: str) -> None:
    url = url.strip()
    # niente opzioni git camuffate da URL (-o...) ne' trasporti che eseguono comandi (ext::)
    if not url or url.startswith("-") or "::" in url or any(c.isspace() for c in url):
        raise BukmarksError(f"URL del remote non valido: {url!r}")
    ensure_repo(home)
    verb = "set-url" if remote_url(home) else "add"
    git(home, "remote", verb, "origin", url)


def _identity_args(home: Path) -> list[str]:
    args: list[str] = []
    if not git(home, "config", "user.name", check=False).stdout.strip():
        args += ["-c", "user.name=bukmarks"]
    if not git(home, "config", "user.email", check=False).stdout.strip():
        args += ["-c", "user.email=bukmarks@localhost"]
    return args


def commit(home: Path, message: str) -> str | None:
    git(home, "add", "--", FILE_NAME)
    if not git(home, "status", "--porcelain", "--", FILE_NAME).stdout.strip():
        return None
    git(home, *_identity_args(home), "commit", "-q", "-m", message)
    return git(home, "rev-parse", "--short", "HEAD").stdout.strip()


def push(home: Path) -> None:
    git(home, "push", "-q", "-u", "origin", "HEAD")


def autosave(home: Path, message: str) -> SaveResult:
    """Commit e (se c'e' un remote) push. Un push fallito non perde i dati: il commit resta locale."""
    ensure_repo(home)
    res = SaveResult(commit=commit(home, message))
    if remote_url(home):
        try:
            push(home)
            res.pushed = True
        except BukmarksError as e:
            res.pushed, res.error = False, str(e)
    return res


def sync(home: Path) -> str:
    """Pull (rebase) dal remote e push. Ritorna un messaggio di esito."""
    ensure_repo(home)
    if not remote_url(home):
        raise BukmarksError("nessun remote configurato: usa `bukmarks remote <url>`")
    git(home, "fetch", "-q", "origin")
    branch = git(home, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    has_remote_branch = git(home, "rev-parse", "--verify", "-q", f"origin/{branch}", check=False).returncode == 0
    if has_remote_branch:
        has_local = git(home, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0
        if has_local:
            proc = git(home, "pull", "-q", "--rebase", "origin", branch, check=False)
            if proc.returncode != 0:
                git(home, "rebase", "--abort", check=False)
                raise BukmarksError(
                    "conflitto durante il pull, rebase annullato:\n"
                    + (proc.stderr or proc.stdout).strip()
                )
        else:
            git(home, "reset", "-q", "--hard", f"origin/{branch}")
    if git(home, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0:
        push(home)
    return "sincronizzato con origin"


def log(home: Path, n: int = 15) -> list[tuple[str, str, str]]:
    if git(home, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode != 0:
        return []
    out = git(home, "log", f"-{n}", "--date=short", "--pretty=format:%h\x1f%ad\x1f%s").stdout
    return [tuple(line.split("\x1f", 2)) for line in out.splitlines()]  # type: ignore[misc]
