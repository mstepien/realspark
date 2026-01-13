# --- Stage 1: Base (Shared Runtime) ---
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/cache/transformers \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Minimal runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Development (Dev Tools & Tests) ---
FROM base AS development

# Install Dev Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    gnupg \
    sudo \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install all dependencies (Prod + Dev)
COPY requirements.txt requirements-dev.txt ./
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Create non-root user for development
RUN mkdir -p tmp data cache/transformers && \
    useradd -m myuser && \
    echo "myuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    chown -R myuser:myuser /app

USER myuser
COPY --chown=myuser:myuser . .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


# --- Stage 3: Production (Lean Runtime) ---
FROM base AS production

# Install only production dependencies
COPY requirements.txt ./
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN mkdir -p tmp data cache/transformers && \
    useradd -m myuser && \
    chown -R myuser:myuser /app

USER myuser
COPY --chown=myuser:myuser . .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
