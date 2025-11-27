"""Mock VPS configurations for testing different scenarios.

This module provides different VPS configurations for testing:
- VPS without Docker
- VPS with old Python
- VPS with missing packages
"""

from typing import Literal

MockVPSConfig = Literal["default", "no_docker", "old_python", "minimal"]


def get_dockerfile_for_config(config: MockVPSConfig) -> str:
    """Get Dockerfile content for specific configuration.

    Args:
        config: VPS configuration type

    Returns:
        Dockerfile content as string
    """
    if config == "no_docker":
        # Ubuntu with SSH but no Docker
        return """
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH and Python only (no Docker)
RUN apt-get update && apt-get install -y \
    openssh-server \
    python3.11 \
    python3-pip \
    sudo \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH
RUN mkdir /var/run/sshd && \
    mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Allow root login with key authentication
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Create SSH key for testing
RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
"""

    elif config == "old_python":
        # Ubuntu with SSH, Docker, but old Python (3.8)
        return """
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH, old Python, and Docker
RUN apt-get update && apt-get install -y \
    openssh-server \
    python3.8 \
    python3-pip \
    sudo \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Make python3.8 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# Install Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Install Docker Compose
RUN curl -SL "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Configure SSH
RUN mkdir /var/run/sshd && \
    mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
"""

    elif config == "minimal":
        # Minimal Ubuntu with SSH only
        return """
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install only SSH
RUN apt-get update && apt-get install -y \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH
RUN mkdir /var/run/sshd && \
    mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
"""

    else:
        # Default: full-featured VPS (same as Dockerfile.mock-vps)
        return """
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH, Python, and Docker dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    python3.11 \
    python3-pip \
    sudo \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    systemctl \
    && rm -rf /var/lib/apt/lists/*

# Install Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Install Docker Compose
RUN curl -SL "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Configure SSH
RUN mkdir /var/run/sshd && \
    mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
"""


def get_docker_compose_for_config(config: MockVPSConfig, port: int = 2222) -> str:
    """Get docker-compose.yml content for specific configuration.

    Args:
        config: VPS configuration type
        port: SSH port to expose

    Returns:
        docker-compose.yml content as string
    """
    container_suffix = "" if config == "default" else f"-{config}"

    # For non-Docker configs, don't mount Docker socket
    volumes = (
        []
        if config in ["no_docker", "minimal"]
        else [
            "/var/run/docker.sock:/var/run/docker.sock",
            "mock-vps-data:/opt",
        ]
    )

    volumes_section = "\n      - ".join([""] + volumes) if volumes else ""

    # Only enable privileged mode if Docker is needed
    privileged = "true" if config not in ["no_docker", "minimal"] else "false"

    return f"""version: '3.8'

services:
  mock-vps{container_suffix}:
    build:
      context: .
      dockerfile: Dockerfile.mock-vps-{config}
    container_name: telegram-bot-stack-mock-vps{container_suffix}
    privileged: {privileged}
    ports:
      - "{port}:22"
    networks:
      - test-network{volumes_section}
    healthcheck:
      test: ["CMD", "ssh", "-o", "StrictHostKeyChecking=no", "root@localhost", "echo", "ok"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

networks:
  test-network:
    driver: bridge

volumes:
  mock-vps-data:
"""
