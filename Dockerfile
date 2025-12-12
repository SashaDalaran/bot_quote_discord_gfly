# =============================
# Stage 1 — Build environment
# =============================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for building Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency file for layer caching
COPY requirements.txt .

# Upgrade pip and build wheels into a clean isolated directory
RUN pip install --upgrade pip setuptools wheel \
 && pip install --prefix=/install -r requirements.txt


# =============================
# Stage 2 — Runtime environment
# =============================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Minimal OS packages + security hygiene
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Optional: reduce image size by removing CPython test suites
RUN rm -rf /usr/local/lib/python3.11/test \
 && rm -rf /usr/local/lib/python3.11/distutils/tests \
 && rm -rf /usr/local/lib/python3.11/unittest/test

# Create a non-root user
RUN useradd -m bot

WORKDIR /app

# Copy Python dependencies from build stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Ensure correct permissions
RUN chown -R bot:bot /app

USER bot

# Use exec-form for proper signal handling (important on Fly Machines)
ENTRYPOINT ["python", "bot.py"]
