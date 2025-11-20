# Docker Escape Challenge: Asylum Gate Control

## Challenge Description

You find yourself inside a privileged Docker container that controls the final gate of an asylum. The SCADA (Supervisory Control and Data Acquisition) terminal system is running inside the container, but the gate can only be unlocked by retrieving the hidden authorization code stored somewhere in the container.

**Your Objective:** Access the container, find the hidden authorization code, and unlock the final gate using the SCADA terminal.

## Challenge Details

- **Container Type:** Privileged Docker container
- **Service:** SCADA Terminal Interface (Port 9001)
- **User:** `scada_operator` (non-root user with sudo)
- **Password:** `gatekeeper123`
- **Goal:** Find the flag inside the container and unlock the gate

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Basic knowledge of Docker escape techniques

### Building and Running

1. **Build the challenge:**
   ```bash
   docker compose build
   ```

2. **Start the container:**
   ```bash
   docker compose up -d
   ```

3. **Access the SCADA terminal:**
   ```bash
   nc localhost 9001
   # or
   telnet localhost 9001
   ```

### Alternative: Direct Docker Run

```bash
docker build -t asylum-scada .
docker run -d --privileged \
  --name asylum_gate_control \
  -p 9001:9001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --cap-add=SYS_ADMIN \
  --security-opt apparmor:unconfined \
  asylum-scada
```

## SCADA Terminal Commands

Once connected to the terminal, you can use:

- `help` or `?` - Show available commands
- `status` - Display current gate status
- `info` - Show system information
- `unlock <code>` - Attempt to unlock the gate with authorization code
- `lock` - Lock the gate
- `clear` - Clear terminal
- `exit` - Disconnect

## Hints

1. The container runs with `--privileged` flag
2. Docker socket is mounted at `/var/run/docker.sock`
3. The container has `SYS_ADMIN` capabilities
4. The flag is stored somewhere inside the container
5. You may need elevated privileges (sudo/root) to access the flag

## Challenge Techniques to Explore

- **Privilege Escalation:** Use sudo to access root directories
- **File System Exploration:** Find hidden files and directories
- **Docker Socket Escape:** Access Docker socket to control host Docker daemon (optional)
- **Privileged Container Escapes:** Use kernel capabilities and device access (optional)

## Solution Walkthrough

<details>
<summary>Click to reveal solution hints</summary>

1. **Access the container:**
   ```bash
   docker exec -it asylum_gate_control /bin/bash
   ```

2. **Find the flag in the container:**
   - Use `sudo` with password `gatekeeper123` to access root directories
   - Explore hidden directories (like `/root/.asylum/`)
   - Use `find` or `grep` to search for the flag

3. **Unlock the gate:**
   - Read the flag file
   - Connect to SCADA terminal and use `unlock <flag>` or `unlock /path/to/flag`

</details>

## Flag Format

The flag follows the format: `THM{unl0ckth3g4t350fh3ll}`

## Cleanup

To stop and remove the container:

```bash
docker compose down
# or
docker stop asylum_gate_control && docker rm asylum_gate_control
```

## Educational Purpose

This challenge is designed for:
- Learning Docker security
- Understanding container escape techniques
- Practicing privilege escalation in containers
- SCADA/ICS security awareness

**Note:** This challenge is for educational purposes only. Always ensure you have proper authorization before testing security vulnerabilities.
