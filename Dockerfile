# ---------- Stage 1: Build environment ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Only requirements first (cache layer)
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt \
 && rm -rf /root/.cache/pip


# ---------- Stage 2: Final runtime ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# OPTIONAL micro-optimization (чистим тестовые файлы Python)
RUN rm -rf /usr/local/lib/python3.11/test \
 && rm -rf /usr/local/lib/python3.11/distutils/tests \
 && rm -rf /usr/local/lib/python3.11/unittest/test

# Create secure user
RUN useradd -m bot

WORKDIR /app

# Copy installed libs
COPY --from=builder /install /usr/local

# Copy project code
COPY . .

# Fix permissions BEFORE switching user
RUN chown -R bot:bot /app

USER bot

CMD ["python", "bot.py"]
