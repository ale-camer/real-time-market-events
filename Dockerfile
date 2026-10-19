FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy patches and apply faust tracing fix if present
COPY patches/ /app/patches/
RUN if [ -f /app/patches/fix_faust_tracing.py ]; then python3 /app/patches/fix_faust_tracing.py; fi

# Copy source code and configurations
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "-m", "src.api.main"]
