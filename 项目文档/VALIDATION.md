# Validation record

## v1.0.3 (2026-10-04)

The package author and this project's MIT copyright display name were normalized to `dhtfish98`; executable source is unchanged from v1.0.2. Python 3.12.13 installed a wheel built from the staged source, and all 9/9 local tests passed. Installed package metadata reports version `1.0.3` and author `dhtfish98`. The wheel contains five source files byte-identical to this checkout and the current MIT license text.

These are local packaging and test checks; public commit, CI, tag and Release status must be checked against GitHub separately.

## v1.0.2 (2026-10-04)

Python 3.14.6 passed 9/9 local unit and regression tests. Two added tests use synthetic local files to verify that a failed stream construction closes an owned descriptor and preserves the original error if the stream constructor already closed it. This verifies local failure paths only; exact public-commit CI is checked separately.

## Historical v1.0.1 record (2026-10-02)

Version: 1.0.1. Python 3.14.6 passed 7/7 local unit/regression tests. A wheel was built with Python 3.12, installed in a fresh Python 3.12 virtual environment outside the checkout, and its CLI was invoked from outside the source directory.

Installed text/JSON CLI redaction and incomplete-review exit code verified. The wheel contains five package source files plus license and metadata; each packaged source file was byte-compared with the v1.0.1 checkout.

Wheel SHA-256: `062e9acdaf61594739a909db84f7a7094e8d9b1d813af92c70b0cf5a1de0c053`.

The tests cover normal declaration/redaction behavior, input-size limits, direct symlinks, non-regular files and the specific incomplete/error cases found during source review. All credentials are synthetic; PE samples were existing local pip PE32/PE32+ launcher files and were only read.

Regex coverage and false-positive rates are not measured on a broad corpus. Skipped eligible files make the review incomplete. The exact public commit and corresponding GitHub workflow are verified separately in the portfolio index.

CVP eligibility remains OPEN: these technical checks do not establish an actual safeguards-affected task, applicant identity, organization binding or an Anthropic decision.
