FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    vim \
    curl \
    netcat-openbsd \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for Docker socket escape)
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Create docker group and non-root user (to make it more realistic)
RUN groupadd -g 999 docker || true && \
    useradd -m -s /bin/bash scada_operator && \
    echo "scada_operator:gatekeeper123" | chpasswd && \
    usermod -aG sudo,docker scada_operator && \
    echo "scada_operator ALL=(ALL) NOPASSWD: /usr/bin/docker" >> /etc/sudoers

# Create SCADA application directory
RUN mkdir -p /opt/scada && \
    chown scada_operator:scada_operator /opt/scada

# Create unlock code file in a hidden location (requires root/sudo to access)
RUN mkdir -p /root/.asylum && \
    echo "739184627" > /root/.asylum/unlock_code && \
    chmod 600 /root/.asylum/unlock_code

# Copy SCADA application
COPY scada_terminal.py /opt/scada/
COPY gate_controller.sh /opt/scada/
RUN chmod +x /opt/scada/scada_terminal.py /opt/scada/gate_controller.sh && \
    chown scada_operator:scada_operator /opt/scada/*

# Set working directory
WORKDIR /opt/scada

# Switch to non-root user
USER scada_operator

# Expose the SCADA port
EXPOSE 9001

# Run the SCADA terminal
CMD ["python3", "/opt/scada/scada_terminal.py"]
