FROM python:3.13-alpine

# ---------- Environment ----------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- System Dependencies ----------
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

# ---------- Work Directory ----------
WORKDIR /app

# ---------- Install Python Dependencies ----------
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- Copy Project ----------
COPY . .

# ---------- Create Non-Root User ----------
RUN adduser -D appuser
USER appuser

# ---------- Expose Port ----------
EXPOSE 8000

# ---------- Start Application ----------
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
