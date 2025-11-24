# Systemd Service Setup - Asylum SCADA Terminal

This guide explains how to set up the Asylum Gate Control SCADA Terminal to run automatically on system boot using systemd.

## Prerequisites

- Docker installed and running
- Docker Compose installed (`docker compose` or `docker-compose`)
- Service file and docker-compose.yml in the same directory

## Installation Steps

### 1. Copy the Service File

Copy the service file to the systemd directory:

```bash
sudo cp asylum-scada.service /etc/systemd/system/
```

### 2. Update the Working Directory (if needed)

Edit the service file if your challenge directory is different:

```bash
sudo nano /etc/systemd/system/asylum-scada.service
```

Update the `WorkingDirectory` line to match your actual path:
```
WorkingDirectory=/home/ubuntu/scada-final-gate
```

Also, if you're using `docker-compose` (with hyphen) instead of `docker compose`, uncomment the alternative ExecStart/ExecStop lines:

```ini
# Use these if docker-compose (standalone) instead of docker compose (plugin)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
```

### 3. Check Docker Compose Path

Verify where docker compose is installed:

```bash
# For docker compose (plugin)
which docker
# Should show: /usr/bin/docker or /snap/bin/docker

# For docker-compose (standalone)
which docker-compose
# Should show: /usr/bin/docker-compose or /usr/local/bin/docker-compose
```

Update the ExecStart and ExecStop paths in the service file if needed.

### 4. Reload Systemd

After creating/modifying the service file, reload systemd:

```bash
sudo systemctl daemon-reload
```

### 5. Enable the Service

Enable the service to start on boot:

```bash
sudo systemctl enable asylum-scada.service
```

### 6. Start the Service

Start the service immediately (without rebooting):

```bash
sudo systemctl start asylum-scada.service
```

### 7. Check Service Status

Verify the service is running:

```bash
sudo systemctl status asylum-scada.service
```

You should see output like:
```
● asylum-scada.service - Asylum Gate Control SCADA Terminal
     Loaded: loaded (/etc/systemd/system/asylum-scada.service; enabled; vendor preset: enabled)
     Active: active (exited) since ...
```

### 8. Check Container Status

Verify the container is running:

```bash
docker ps | grep asylum_gate_control
```

## Service Management Commands

### Start the service:
```bash
sudo systemctl start asylum-scada.service
```

### Stop the service:
```bash
sudo systemctl stop asylum-scada.service
```

### Restart the service:
```bash
sudo systemctl restart asylum-scada.service
```

### Check service status:
```bash
sudo systemctl status asylum-scada.service
```

### View service logs:
```bash
sudo journalctl -u asylum-scada.service -f
```

### Disable auto-start on boot:
```bash
sudo systemctl disable asylum-scada.service
```

### Enable auto-start on boot:
```bash
sudo systemctl enable asylum-scada.service
```

## Troubleshooting

### Service fails to start

1. **Check Docker is running:**
   ```bash
   sudo systemctl status docker
   ```

2. **Check service logs:**
   ```bash
   sudo journalctl -u asylum-scada.service -n 50
   ```

3. **Verify working directory exists:**
   ```bash
   ls -la /home/ubuntu/scada-final-gate
   ```

4. **Test docker compose manually:**
   ```bash
   cd /home/ubuntu/scada-final-gate
   docker compose up -d
   ```

### Container not starting

1. **Check Docker Compose logs:**
   ```bash
   cd /home/ubuntu/scada-final-gate
   docker compose logs
   ```

2. **Check container logs:**
   ```bash
   docker logs asylum_gate_control
   ```

### Service runs but container stops

The service uses `Type=oneshot` with `RemainAfterExit=yes`, which means it starts the container and then exits (but remains marked as active). This is normal behavior. If the container stops, check:

```bash
docker ps -a | grep asylum
docker logs asylum_gate_control
```

## Manual Service File Location

The service file is located at:
```
/etc/systemd/system/asylum-scada.service
```

To edit it:
```bash
sudo nano /etc/systemd/system/asylum-scada.service
```

After editing, always reload systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl restart asylum-scada.service
```

## Testing on Boot

To verify it works on boot:

1. Reboot the system:
   ```bash
   sudo reboot
   ```

2. After reboot, check if the service started:
   ```bash
   sudo systemctl status asylum-scada.service
   docker ps | grep asylum
   ```

3. Test the SCADA terminal:
   ```bash
   nc localhost 9001
   # When prompted, enter Part 1 flag: THM{Y0u_h4ve_b3en_j3stered_739138}
   ```

## Notes

- The service will automatically start Docker containers on boot
- If Docker is not available at boot time, the service will wait for it (due to `Requires=docker.service`)
- The service runs as root (required for Docker operations)
- The `Restart=on-failure` directive will attempt to restart if the service fails



