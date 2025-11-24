# Docker Escape Challenge: Asylum Gate Control - Part 2

## Challenge Description

This is **Part 2** of the Asylum challenge series. You've already gained initial access as `svc_vidops` user from Part 1 and retrieved the `user.txt` flag. Now you need to escape from a privileged Docker container that controls the final gate of the asylum. The SCADA (Supervisory Control and Data Acquisition) terminal system is running inside the container, but you must authenticate with your Part 1 flag to access it, and then retrieve the hidden authorization code to unlock the gate.

**Your Objective:** Access the privileged Docker container, perform Docker escape to retrieve the numeric unlock code, authenticate to the SCADA terminal with your Part 1 flag, and unlock the final gate.

## Challenge Details

- **Part 1 Connection:** You start with shell access as `svc_vidops` user (from Part 1)
- **Part 1 Flag Required:** `THM{Y0u_h4ve_b3en_j3stered_739138}` (for SCADA authentication)
- **Container Type:** Privileged Docker container
- **Service:** SCADA Terminal Interface (Port 9001) - Requires authentication
- **Container User:** `scada_operator` (non-root user with sudo)
- **Password:** `gatekeeper123`
- **Goal:** Perform Docker escape, retrieve numeric unlock code, authenticate to SCADA terminal, and unlock the gate

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
   ```
   
   **Important:** The SCADA terminal requires authentication with your Part 1 flag:
   - When prompted for authorization token, enter: `THM{Y0u_h4ve_b3en_j3stered_739138}`
   - Only after authentication will you have access to SCADA commands

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

## SCADA Terminal Access

### Authentication Required

The SCADA terminal requires authentication using the flag from Part 1:
- **Part 1 Flag:** `THM{Y0u_h4ve_b3en_j3stered_739138}`

Connect to the terminal:
```bash
nc localhost 9001
```

You'll be prompted:
```
[AUTH] Enter authorization token: 
```

Enter the Part 1 flag to gain access.

### SCADA Terminal Commands

Once authenticated, you can use:

- `help` or `?` - Show available commands
- `status` - Display current gate status
- `info` - Show system information
- `unlock <code>` - Attempt to unlock the gate with numeric authorization code
- `lock` - Lock the gate
- `clear` - Clear terminal
- `exit` - Disconnect

## Hints

1. The container runs with `--privileged` flag
2. Docker socket is mounted at `/var/run/docker.sock`
3. The container has `SYS_ADMIN` capabilities
4. The numeric unlock code is stored somewhere inside the container
5. You may need elevated privileges (sudo/root) to access the unlock code

## Challenge Techniques to Explore

- **Docker Socket Escape:** Use Docker socket to execute commands as root inside container
- **Privileged Container Escapes:** Exploit kernel capabilities and device access
- **Container Access:** Gain access to the privileged container from the host
- **Authentication Bypass:** Use Part 1 flag to authenticate to SCADA terminal

## Solution Walkthrough

<details>
<summary>Click to reveal solution hints</summary>

1. **Access the container:**
   ```bash
   docker exec -it asylum_gate_control /bin/bash
   ```

2. **Perform Docker escape to get unlock code:**
   - Use Docker socket to execute commands as root: `sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/unlock_code`
   - Alternative: Use sudo with password `gatekeeper123` to access `/root/.asylum/unlock_code`

3. **Authenticate to SCADA terminal:**
   - Connect: `nc localhost 9001`
   - Enter Part 1 flag when prompted: `THM{Y0u_h4ve_b3en_j3stered_739138}`

4. **Unlock the gate:**
   - Use the unlock command with the numeric code: `unlock 739184627`

</details>

## Flags and Codes

- **Part 1 (user.txt):** `THM{Y0u_h4ve_b3en_j3stered_739138}` - Required for SCADA authentication
- **Part 2 (unlock code):** Numeric code stored at `/root/.asylum/unlock_code` - Required to unlock the gate

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
