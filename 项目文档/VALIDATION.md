# Current validation record: 2026-10-02

Current version: 1.0.1. Python 3.14.6 passed 7/7 local unit/regression tests. A wheel was built with Python 3.12, installed in a fresh Python 3.12 virtual environment outside the checkout, and its CLI was invoked from outside the source directory.

Installed text/JSON CLI redaction and incomplete-review exit code verified. The wheel contains five package source files plus license and metadata; each packaged source file was byte-compared with the current checkout.

Wheel SHA-256: `062e9acdaf61594739a909db84f7a7094e8d9b1d813af92c70b0cf5a1de0c053`.

The tests cover normal declaration/redaction behavior, input-size limits, direct symlinks, non-regular files and the specific incomplete/error cases found during source review. All credentials are synthetic; PE samples were existing local pip PE32/PE32+ launcher files and were only read.

Regex coverage and false-positive rates are not measured on a broad corpus. Skipped eligible files make the review incomplete. The exact public commit and corresponding GitHub workflow are verified separately in the portfolio index.

CVP eligibility remains OPEN: these technical checks do not establish an actual safeguards-affected task, applicant identity, organization binding or an Anthropic decision.
