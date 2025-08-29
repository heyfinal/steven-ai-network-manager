# AI Systems Manager - Bulletproof Docker Image
# Multi-stage build for production deployment

FROM python:3.11-slim as base

# System dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    openssh-client \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Install docker-compose CLI only if truly required
# RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
#     && chmod +x /usr/local/bin/docker-compose

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs

# Copy application code
COPY src/ ./src/
# Do not bake compose files into the image

# Set Python path
ENV PYTHONPATH=/app/src

# Create non-privileged app user
RUN useradd -m -s /bin/bash app \
    && chown -R app:app /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5001')" || exit 1

# Switch to non-root app user
USER app

# Expose ports
EXPOSE 5001 8888 9090

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
