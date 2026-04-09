# ---------- Stage 1: Builder ----------
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

# Install Python dependencies into custom location
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---------- Stage 2: Final ----------
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Only runtime dependencies (LIGHT)
RUN apk add --no-cache \
    postgresql-libs \
    libffi

# Copy installed packages from builder (no gcc, no build deps)
COPY --from=builder /install /usr/local

# Copy project
COPY . .

# Create non-root user
RUN adduser -D appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
