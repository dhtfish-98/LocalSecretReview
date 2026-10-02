"""Command line interface that never prints the matched value or source snippet."""

from __future__ import annotations

import argparse
import json
from .scanner import DEFAULT_MAX_BYTES, scan_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline, redacted review of a local source tree")
    parser.add_argument("path", help="local file or directory owned by the operator")
    parser.add_argument("--json", action="store_true", help="emit finding metadata as JSON")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="per-file read limit")
    args = parser.parse_args(argv)
    try:
        result = scan_path(args.path, max_bytes=args.max_bytes)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps({
            "findings": [finding.export() for finding in result.findings],
            "scanned_files": result.scanned_files,
            "skipped_files": result.skipped_files,
        }, sort_keys=True))
    else:
        for finding in result.findings:
            print(f"{finding.path}:{finding.line}:{finding.column}: {finding.rule} ({finding.severity}); value redacted")
        print(f"Scanned {result.scanned_files} files; skipped {result.skipped_files}; findings {len(result.findings)}")
    return 2 if result.skipped_files else (1 if result.findings else 0)
