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

# Patch faust-streaming bug: tracing.py crashes when tracer is None (NoneType.start_span)
COPY patches/fix_faust_tracing.py /tmp/fix_faust_tracing.py
RUN python3 /tmp/fix_faust_tracing.py

# Copy source code and alembic configurations
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Default command will be overridden in docker-compose
CMD ["python", "-m", "src.api.main"]
