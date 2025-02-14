# Stage 1: Build stage
FROM python:3.12-slim as builder

ENV POETRY_VERSION=2.0.0
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
ENV POETRY_VIRTUALENVS_IN_PROJECT=1

# Install build dependencies if needed (uncomment below)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# Install Poetry in isolated virtual environment
RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install --no-cache-dir poetry==$POETRY_VERSION

# Add Poetry to PATH
ENV PATH="$POETRY_VENV/bin:$PATH"

WORKDIR /app

# Copy dependency specifications
COPY pyproject.toml poetry.lock ./

# Install project dependencies (production only)
RUN poetry install --without dev --no-directory

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv

# Copy application code
COPY . .

# Add the source directory to PYTHONPATH so imports resolve correctly
ENV PYTHONPATH="/app/src"

# Copy the entrypoint script into the image and set execute permission
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 3100

ENTRYPOINT ["/entrypoint.sh"]