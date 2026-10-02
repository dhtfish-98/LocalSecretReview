"""Inspect local source without returning or retaining matched secret values."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
from typing import Iterable
from .local_input import read_local_file

SOURCE_SUFFIXES = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".json", ".py", ".toml", ".yaml", ".yml"}
IGNORED_DIRS = {".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", ".ruff_cache", "node_modules", "vendor", "dist", "build", "__pycache__", ".venv", "venv"}
DEFAULT_MAX_BYTES = 1_048_576
MAX_ALLOWED_BYTES = 16 * 1_048_576

# Deliberately narrow patterns: a match is a review prompt, not proof of a valid credential.
RULES = (
    ("private-key-header", "high", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
    ("github-token-shape", "high", re.compile(r"(?<![A-Za-z0-9_])(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}(?![A-Za-z0-9_])")),
    ("aws-access-key-shape", "medium", re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}(?![A-Z0-9])")),
    ("literal-credential-assignment", "medium", re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|token|secret|password|passwd)\b['\"`]?\s*[:=]\s*['\"`]?([A-Za-z0-9/+._=-]{12,})",
        re.IGNORECASE,
    )),
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    column: int
    rule: str
    severity: str

    def export(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class ScanResult:
    findings: tuple[Finding, ...]
    scanned_files: int
    skipped_files: int


def _is_source(path: Path) -> bool:
    return path.suffix.lower() in SOURCE_SUFFIXES or path.name == ".env" or path.name.startswith(".env.")


def _files(root: Path) -> Iterable[tuple[Path, str]]:
    if root.is_symlink():
        raise ValueError("symbolic-link input is not accepted")
    if root.is_file():
        yield root, root.name
        return
    if not root.is_dir():
        raise ValueError("input must be an existing local file or directory")
    def fail(error: OSError) -> None:
        raise error

    for base, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        dirs[:] = sorted(name for name in dirs if name not in IGNORED_DIRS and not (Path(base) / name).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            if not path.is_symlink() and _is_source(path):
                yield path, path.relative_to(root).as_posix()


def scan_path(root: str | Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> ScanResult:
    """Return finding metadata only. Matched values never leave this function."""
    if not 1 <= max_bytes <= MAX_ALLOWED_BYTES:
        raise ValueError("max_bytes must be between 1 and 16777216")
    source = Path(root).expanduser()
    found: list[Finding] = []
    scanned = skipped = 0
    for path, label in _files(source):
        try:
            content = read_local_file(path, max_bytes)
            if b"\x00" in content:
                skipped += 1
                continue
            text = content.decode("utf-8")
        except (OSError, UnicodeError, ValueError):
            skipped += 1
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), 1):
            for rule, severity, pattern in RULES:
                for match in pattern.finditer(line):
                    found.append(Finding(label, number, match.start() + 1, rule, severity))
    return ScanResult(tuple(sorted(set(found))), scanned, skipped)
