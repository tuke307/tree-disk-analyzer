# syntax=docker/dockerfile:1.7

# Stage 1: build application with uv
FROM python:3.12-slim AS builder

# Copy uv binaries from the official image (pin to a specific release)
COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install only dependency tree first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-editable

# Copy the remainder of the source and install the project itself
COPY . .
RUN uv sync --locked --no-editable

# Stage 2: runtime image with pre-synced virtual environment
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment and application payload from builder
COPY --from=builder /app /app

# Ensure entrypoint is executable and the venv is on PATH
RUN chmod +x /app/entrypoint.sh
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 3100

ENTRYPOINT ["/app/entrypoint.sh"]