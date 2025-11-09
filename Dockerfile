FROM python:3.11-slim AS base

ARG POETRY_VERSION=2.2.1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install poetry
RUN pip install poetry==${POETRY_VERSION}
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry lock && poetry install --no-root --no-dev

# Copy application code
COPY ticketer/ ./ticketer/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "ticketer.main:app", "--host", "0.0.0.0", "--port", "8000"]

