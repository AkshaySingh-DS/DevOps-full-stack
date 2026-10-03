# Phase 3 — GitHub Actions CI

## Objective

Create one CI pipeline that validates the application and the production Docker
build before a change can be considered merge-ready.

This phase is deliberately limited to **CI**. There is no deployment, container
registry push, GitOps update, Argo CD integration, SonarQube gate, Trivy scan, or
cloud authentication yet. Those responsibilities belong to later phases.

## Pipeline

```text
Pull Request / push to main
            |
            v
       Checkout source
            |
            v
       Setup Python 3.10.13
            |
            v
       Install dependencies
            |
            v
       pip check
            |
            v
       Python compile check
            |
            v
       Ruff lint
            |
            v
       PostgreSQL service
            |
            v
       Alembic upgrade head
            |
            v
       Alembic migration check
            |
            v
       Pytest + coverage >= 80%
            |
            v
       Coverage artifact
            |
            v
       Docker Buildx
            |
            v
       Production image build
       (NO PUSH)
            |
            v
          CI PASS
```

The workflow is intentionally a **single job with sequential gates**. GitHub
Actions stops the job when a required command fails, which makes the failure
point obvious in an interview and keeps the project simple.

## Why these gates exist

### 1. Dependency installation + `pip check`

The workflow installs the same development dependency set used by the project,
then verifies that the installed package graph is internally consistent.

This is dependency consistency checking, not vulnerability scanning. Vulnerability
scanning is deliberately deferred to Phase 4.

### 2. Python compilation check

```bash
python -m compileall -q app migrations tests
```

This catches basic syntax/import-compilation problems early and costs almost
nothing in CI time.

### 3. Ruff lint

```bash
python -m ruff check app migrations tests
```

Linting gives fast feedback before the test suite and prevents obvious code-quality
issues from progressing further in the pipeline.

### 4. PostgreSQL service container

CI uses a real PostgreSQL service rather than relying only on SQLite. This keeps
the automated test environment close to the application's intended production
database engine.

### 5. Alembic migration gate

```bash
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. alembic check
```

This proves that the migration chain can build the database and that SQLAlchemy
metadata is not silently drifting away from the migration history.

### 6. Pytest + coverage gate

```bash
python -m pytest -q --cov=app --cov-fail-under=80
```

The 80% threshold is a deliberately modest quality floor for this small demo
application. It is a guardrail, not a claim that 80% coverage equals production
quality.

The workflow also stores `coverage.xml` as a short-lived GitHub Actions artifact.
That gives later SonarQube work a ready-made coverage report without redesigning
the test stage.

### 7. Docker build gate

The pipeline builds the Phase 2 multi-stage production Dockerfile, but does **not**
push it anywhere.

That creates the following boundary:

```text
CI phase
  |
  +-- build image  -> YES
  |
  +-- scan image   -> Phase 4
  |
  +-- push image   -> later registry/CD phase
  ```

This keeps Phase 3 focused on proving that source code and the production image
can be built successfully.

## Why the image is not pushed yet

The project roadmap deliberately separates:

```text
Phase 3
CI validation

Phase 4
security gates

Phase 6+
registry + GitOps/CD
```

Pushing an image before the security gates are introduced would weaken the story
we are building. Eventually the successful path will become:

```text
Lint
  -> Tests
  -> Quality
  -> Security
  -> Image build
  -> Image scan
  -> Push image
```

## GitHub Actions hardening

The workflow uses several platform-engineering practices:

- `permissions: contents: read` to keep the default GitHub token least-privileged.
- `persist-credentials: false` on checkout so the repository token is not left in
  the local Git configuration.
- Action references are pinned to immutable commit SHAs where the release SHA was
  verified. `setup-buildx-action` is currently referenced by its release tag and is
  a candidate for centralized SHA pinning later.
- `concurrency` cancels stale in-progress PR runs so runner minutes are not wasted
  testing superseded commits.
- CI secrets are not required. The PostgreSQL credentials are disposable values
  used only by the ephemeral service container.
- A timeout prevents a stuck workflow from consuming runner time indefinitely.

## Deliberate non-goals for Phase 3

Do not add these yet:

- SonarQube
- Trivy
- pip-audit
- Dependabot configuration
- GitHub Secret Scanning configuration
- Container registry authentication
- image push
- Helm
- Kubernetes
- Argo CD
- Terraform
- AWS credentials / OIDC

Those are separate architecture decisions in later phases.

## Interview story

### Problem

We needed a repeatable way to prevent broken application changes and broken
container builds from progressing into the platform.

### Investigation

Local testing alone depends on each developer's workstation, installed packages,
and database state. We needed a clean, repeatable environment in GitHub.

### Options

1. Run only unit tests.
2. Add linting, database migration validation, coverage, and Docker build validation.
3. Build a large multi-workflow CI/CD system immediately.

### Decision

Use one sequential GitHub Actions CI workflow with explicit gates. Keep deployment
and security scanning outside this phase so each later phase has a clear purpose.

### Implementation

```text
GitHub PR / main push
        |
        +--> dependency consistency
        +--> syntax check
        +--> lint
        +--> PostgreSQL migration validation
        +--> pytest + coverage gate
        +--> Docker build
```

### Result

A change must successfully pass the complete CI chain before it is considered
ready to move into the later security and delivery pipeline.

### Trade-off

A single sequential job is easier to understand and gives a clean failure story,
but it is slower than a highly parallelized enterprise pipeline.

### What I'd change at scale

For a larger organization, split independent lanes into jobs (lint, unit tests,
integration tests, image build, and security) and make later gates depend on the
required upstream jobs. Add remote build caching, test sharding, reusable workflows,
central action pinning, policy enforcement, and ephemeral preview environments.
