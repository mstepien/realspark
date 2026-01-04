# Preffered way would be to use an official Python runtime as a parent image
#FROM python:3.10-slim
#But we will go with 3.10-buster as it is compatible with the older docker v19
FROM python:3.10-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/cache/transformers

# Set work directory
WORKDIR /app

# Install system dependencies (python:3.10-slim)
#RUN apt-get update && apt-get install -y --no-install-recommends \
# Install system dependencies (python:3.10-buster handling archived buster repos)
RUN sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .

# Install CPU-only torch first to avoid massive CUDA downloads
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --default-timeout=1000 --retries 10 --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p tmp data cache/transformers

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
