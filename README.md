# LocalSecretReview

LocalSecretReview checks a source tree you own for a few common credential shapes and reports **locations only**. It never fetches a URL, tests a credential, or prints a matched value or source snippet. The implementation uses the Python standard library and has no runtime dependencies.

```sh
python -m pip install .
local-secret-review /path/to/your/repository
local-secret-review /path/to/your/repository --json
```

Exit code 0 means no findings, 1 means at least one finding, and 2 means invalid input. A finding is a review prompt; it does not prove a credential is valid, exposed on a server, or exploitable.

The scanner examines local `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.json`, `.py`, `.toml`, `.yaml`, `.yml`, `.env` and `.env.*` files. It skips symbolic links, common generated/vendor directories, binary files, invalid UTF-8, and files over 1 MiB by default. `--max-bytes` changes the per-file limit up to 16 MiB. It does not search git history or compressed files. An explicitly named regular file is examined regardless of its suffix.

Current rules flag private-key headers, selected GitHub token shapes, AWS access-key ID shapes, and literal credential assignments. This intentionally small ruleset has false positives and false negatives. No matched bytes, snippets, hashes, or context are stored in `Finding` objects or exported reports. Review the indicated source files locally and rotate any actual exposed credentials through their provider's normal process.

## Verification

```sh
python -m unittest discover -s tests -v
python -m compileall -q src
```

The tests use synthetic local files and check that plain and JSON output never contain their synthetic token values. See [VALIDATION.md](VALIDATION.md) for the measured result and its limits.

## Provenance and scope

This is a new, small implementation for offline defensive code review. Its code is separate from the older, attributed SecretCanopy/SecretFinder derivative. See [ORIGIN.md](ORIGIN.md) for the relationship. Use it only on source you own or have permission to inspect. Repository publication and passing tests do not establish CVP eligibility or approval. Anthropic's [CVP guidance](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) asks for a legitimate defensive use case affected by cyber safeguards.
