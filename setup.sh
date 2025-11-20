#!/bin/bash

echo "=========================================="
echo "  Asylum Gate Control"
echo "=========================================="
echo ""

# Flag is created inside the container during build

# Build the Docker image
echo "Building Docker image..."
# Try docker compose (plugin) first, fallback to docker-compose (standalone)
if docker compose version &>/dev/null; then
    docker compose build
else
    docker-compose build
fi

# Start the container
echo ""
echo "Starting privileged container..."
# Try docker compose (plugin) first, fallback to docker-compose (standalone)
if docker compose version &>/dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for container to be ready
echo ""
echo "Waiting for SCADA terminal to initialize..."
sleep 3

# Check if container is running
if docker ps | grep -q asylum_gate_control; then
    echo "[✓] Container is running"
    echo ""
    echo "=========================================="
    echo "  Challenge is ready!"
    echo "=========================================="
    echo ""
    echo "Connect to the SCADA terminal with:"
    echo "  nc localhost 9001"
    echo "  or"
    echo "  telnet localhost 9001"
    echo ""
    echo "Or access the container shell with:"
    echo "  docker exec -it asylum_gate_control /bin/bash"
    echo ""
else
    echo "[✗] Container failed to start. Check logs with:"
    if docker compose version &>/dev/null; then
        echo "  docker compose logs"
    else
        echo "  docker-compose logs"
    fi
fi
