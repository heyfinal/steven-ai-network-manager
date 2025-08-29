# AI Systems Manager - Bulletproof Docker Image
# Multi-stage build for production deployment

FROM python:3.11-slim as base

# System dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    htop \
    iotop \
    net-tools \
    procps \
    sudo \
    systemd \
    systemctl \
    docker.io \
    docker-compose \
    openssh-client \
    git \
    vim \
    nano \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose (latest version)
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs

# Copy application code
COPY src/ ./src/
COPY docker-compose.yml .

# Set Python path
ENV PYTHONPATH=/app/src

# Create admin user daniel with sudo privileges (HARDCODED)
RUN useradd -m -s /bin/bash daniel \
    && echo "daniel:werds" | chpasswd \
    && usermod -aG sudo daniel \
    && echo "daniel ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set ownership
RUN chown -R daniel:daniel /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5001')" || exit 1

# Switch to daniel user (admin)
USER daniel

# Expose ports
EXPOSE 5001 8888 9090

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]