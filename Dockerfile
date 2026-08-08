FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy source code and alembic configurations
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Default command will be overridden in docker-compose
CMD ["python", "-m", "src.api.main"]
