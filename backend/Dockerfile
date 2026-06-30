# syntax=docker/dockerfile:1

# Build a locked virtual environment separately so the runtime image excludes uv and build caches.
FROM ghcr.io/astral-sh/uv:0.9.18 AS uv

FROM python:3.12-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./

# The backend is an application rather than an installable package, so only locked dependencies
# belong in the image environment.
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# A dedicated unprivileged identity limits the impact of an application compromise.
RUN addgroup --system banking && adduser --system --ingroup banking banking

COPY --from=builder --chown=banking:banking /app/.venv /app/.venv
COPY --chown=banking:banking alembic.ini ./
COPY --chown=banking:banking alembic ./alembic
COPY --chown=banking:banking app ./app

USER banking

EXPOSE 8000

# Migration and seed commands are explicit deploy jobs; the web process only serves HTTP.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
