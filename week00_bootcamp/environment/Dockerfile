FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    wget \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/class

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Runtime workspace for bind-mounted course files.
RUN mkdir -p /workspace

# SSH setup for remote development (VSCode / Antigravity).
# Removed password configuration and deleted password for student user.
RUN useradd -m -s /bin/bash student && \
    passwd -d student && \
    mkdir -p /var/run/sshd /home/student/.ssh && \
    chown -R student:student /home/student/.ssh && \
    chmod 700 /home/student/.ssh && \
    ln -s /workspace /home/student/workspace


# Configure SSH strictly for development environment
RUN echo "StrictModes no" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication no" >> /etc/ssh/sshd_config


WORKDIR /workspace
VOLUME ["/workspace"]
EXPOSE 22

# Example run:
# docker run --rm -it -v ${PWD}:/workspace class python environment/test_setup.py
# SSH mode (recommended for class):
# docker compose -f environment/docker-compose.yml up -d
CMD ["/usr/sbin/sshd", "-D", "-e"]