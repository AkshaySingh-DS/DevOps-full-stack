# Phase 2 training baseline:
# Python 3.10.13 is intentionally old for the security-scanning exercise.
# Do NOT use this baseline for production after Phase 4 remediation.
ARG PYTHON_VERSION=3.10.13

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

#ike the cd command in Linux.
WORKDIR /build

COPY requirements-runtime.txt ./

# Install runtime dependencies into a separate directory so the final image
# does not need compilers or package-manager caches.
# install the packages under /install unlike normal python site-packages
RUN python -m pip install \
        --no-cache-dir \
        --prefix=/install \
        -r requirements-runtime.txt

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

#Normally Python can create .pyc files containing compiled Python bytecode
#below will help not don't create .pyc files and Docker logs appear immediately:
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy only installed runtime packages from the builder stage.
COPY --from=builder /install /usr/local

# Run the API as a dedicated non-root user, we don't want the API to run as Linux root.
# Creates a Linux group, a Linux user, Create a home directory, 
RUN groupadd --system --gid 10001 orderflow \
    && useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/orderflow orderflow \
    && chown -R orderflow:orderflow /app


COPY --chown=orderflow:orderflow app ./app
COPY --chown=orderflow:orderflow migrations ./migrations
COPY --chown=orderflow:orderflow alembic.ini ./alembic.ini

USER orderflow

EXPOSE 8000

# Container health check: process-level health only.
# Database readiness remains the responsibility of /ready.
# If it fails 3 times, mark the container as unhealthy, Each health check is allowed to take at most 5 seconds.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

# run the beklow command when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]%