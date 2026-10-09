# Phase 2 — Security Baseline

## Intentional baseline

Phase 2 intentionally uses `python:3.10.13-slim-bookworm` as a training baseline.
The goal is to create a reproducible container that can later demonstrate image
vulnerability detection and remediation with Trivy.

Python 3.10.13 reached end-of-life on October 1, 2026. Python 3.10.14 later
included security fixes for CVE-2024-0450 and the bundled Expat update for
CVE-2023-52425, among other changes. Therefore this image is intentionally not
a production security target.

## Important boundary

This is a controlled lab baseline for the OrderFlow project. Do not deploy it
to an internet-facing production environment.

## Expected story in later phases

1. Build this baseline image.
2. Scan it with Trivy in Phase 4.
3. Record the actual findings and severity reported by the scanner.
4. Upgrade the Python/base image to a supported, patched version.
5. Rebuild and scan again.
6. Use the before/after scan as the project's shift-left security example.

Do not hard-code a vulnerability count in documentation. The exact findings are
scanner- and database-version dependent and should be captured from the Trivy
run used by the project.
