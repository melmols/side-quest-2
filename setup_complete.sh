#!/bin/bash

echo "=========================================="
echo "  Complete Challenge Setup"
echo "  RCE Entry Point + Docker Escape Challenge"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt update
    sudo apt install -y python3
fi

# ============================================
# Part 1: Setup RCE Entry Point (Port 8080)
# ============================================
echo "Setting up RCE Entry Point..."

cat > /tmp/rce_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import subprocess

class RCEHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path.startswith('/execute?'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            cmd = params.get('cmd', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if cmd:
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
                    self.wfile.write(result)
                except subprocess.TimeoutExpired:
                    self.wfile.write(b'Command timeout')
                except Exception as e:
                    self.wfile.write(str(e).encode())
            else:
                self.wfile.write(b'Usage: /execute?cmd=<command>')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
<!DOCTYPE html>
<html><head><title>System Monitor</title></head>
<body><h1>System Monitor</h1>
<p>Execute: <code>/execute?cmd=&lt;command&gt;</code></p>
<p>Examples:</p>
<ul>
<li><a href="/execute?cmd=whoami">/execute?cmd=whoami</a></li>
<li><a href="/execute?cmd=id">/execute?cmd=id</a></li>
</ul>
</body></html>
            ''')

chmod +x /tmp/rce_server.py

# Create systemd service for RCE entry point
sudo bash -c 'cat > /etc/systemd/system/rce-entry.service << EOF
[Unit]
Description=RCE Entry Point Server
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /tmp/rce_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable rce-entry.service
sudo systemctl start rce-entry.service

sleep 2
if sudo systemctl is-active --quiet rce-entry.service; then
    echo "[✓] RCE entry point service is running on port 8080"
else
    echo "[✗] RCE entry point service failed to start"
fi

# ============================================
# Part 2: Setup Docker Escape Challenge
# ============================================
echo ""
echo "Setting up Docker Escape Challenge..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "[!] Warning: docker-compose.yml not found in current directory"
    echo "[!] Make sure you're in the challenge directory"
fi

# Build the Docker image
echo "Building Docker image..."
if docker compose version &>/dev/null; then
    docker compose build
else
    docker-compose build
fi

# Start the container
echo ""
echo "Starting privileged container..."
if docker compose version &>/dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for container to be ready
echo ""
echo "Waiting for SCADA terminal to initialize..."
sleep 3

# ============================================
# Summary
# ============================================
echo ""
echo "=========================================="
echo "  Challenge Setup Complete!"
echo "=========================================="
echo ""

IP=$(hostname -I | awk '{print $1}')

echo "RCE Entry Point (Port 8080):"
echo "  http://${IP}:8080/execute?cmd=whoami"
echo "  curl \"http://${IP}:8080/execute?cmd=id\""
echo ""

# Check if Docker challenge is running
if docker ps | grep -q asylum_gate_control; then
    echo "SCADA Terminal (Port 9001):"
    echo "  nc ${IP} 9001"
    echo "  telnet ${IP} 9001"
    echo ""
    echo "Container Access:"
    echo "  docker exec -it asylum_gate_control /bin/bash"
    echo ""
else
    echo "[!] Docker challenge container is not running"
    echo "[!] Check logs with: docker compose logs"
    echo ""
fi

echo "Service Management:"
echo "  sudo systemctl status rce-entry.service"
echo "  sudo systemctl status asylum-scada.service  # (if you set it up)"
echo ""
echo "Challenge Flow:"
echo "  1. Get RCE via: http://${IP}:8080/execute?cmd=..."
echo "  2. Get reverse shell"
echo "  3. Access Docker challenge: nc localhost 9001"
echo "  4. Perform Docker escape to get flag"
echo "  5. Unlock gate in SCADA terminal"
echo ""

