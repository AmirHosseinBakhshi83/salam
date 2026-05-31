# ── build stage: install dependencies ──────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps needed to compile some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ── runtime stage: lean final image ────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Only the runtime lib (libpq), not the compiler
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install wheels built in previous stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links /wheels /wheels/*.whl

# Copy source
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Non-root user for security
RUN addgroup --system django && adduser --system --ingroup django django
USER django

EXPOSE 8000

CMD ["gunicorn", "myproject.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "60"]