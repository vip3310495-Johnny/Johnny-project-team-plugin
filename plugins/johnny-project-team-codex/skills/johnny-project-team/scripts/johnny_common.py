"""Shared primitives for project-scoped Johnny gates."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

STATE_DIR = ".johnny"


def run_git(project: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def git_root(project: Path) -> Path:
    return Path(run_git(project.resolve(), "rev-parse", "--show-toplevel")).resolve()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def append_jsonl(path: Path, value: Any) -> None:
    """Append one durable UTF-8 JSON record without rewriting prior history."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def state_lock(project: Path, timeout: float = 5.0) -> Iterator[None]:
    """Cross-platform exclusive byte-range lock with bounded waiting."""
    lock_path = project / STATE_DIR / "state.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    deadline = time.monotonic() + timeout
    acquired = False
    try:
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    if handle.tell() == os.fstat(handle.fileno()).st_size == 0:
                        handle.write(b"\0")
                        handle.flush()
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except (OSError, IOError):
                if time.monotonic() >= deadline:
                    raise TimeoutError("Johnny state lock timed out")
                time.sleep(0.05)
        yield
    finally:
        try:
            if acquired:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def is_enabled(project: Path) -> bool:
    marker = read_json(project / STATE_DIR / "enabled.json", {})
    return bool(marker and marker.get("enabled") is True)


def staged_tree(project: Path) -> str:
    return run_git(project, "write-tree")


def subject_tree(project: Path, product_paths: list[str]) -> str:
    """Hash the staged product subset configured by the project."""
    normalized = sorted({value.strip().replace("\\", "/") for value in product_paths if value.strip()})
    if not normalized:
        raise ValueError("config.product_paths must contain at least one path")
    listing = run_git(project, "ls-files", "--stage", "--", *normalized)
    payload = ("\n".join(normalized) + "\n--INDEX--\n" + listing + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
