FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install `uv` (used for dependency installation).
RUN pip install --no-cache-dir uv

# Create a dedicated virtual environment to keep runtime image small and clean.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv

# Copy dependency manifests first for better Docker layer caching.
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Install only runtime dependencies (disable dev dependency group).
# `--no-install-project` avoids trying to build/install the project package.
RUN uv sync --frozen --no-dev --no-install-project --active


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app /app/app

EXPOSE 8000

ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
