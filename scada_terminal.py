#!/usr/bin/env python3
"""
Asylum Gate Control System - SCADA Terminal
Authorized Personnel Only
"""

import socket
import threading
import sys
import subprocess
import os

# Banner
BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║     ASYLUM GATE CONTROL SYSTEM - SCADA TERMINAL v2.1          ║
║              [AUTHORIZED PERSONNEL ONLY]                      ║
╚═══════════════════════════════════════════════════════════════╝

[!] WARNING: This system controls critical infrastructure
[!] All access attempts are logged and monitored
[!] Unauthorized access will result in immediate termination

Initializing terminal connection...
"""

# Gate states
GATE_STATUS = "LOCKED"
GATE_CODE = "/etc/hostname"  # Flag location hint
HOSTNAME_FILE = "/etc/hostname"

def print_prompt():
    """Print the SCADA prompt"""
    return f"\n[SCADA-ASYLUM-GATE] #{GATE_STATUS}> "

def get_gate_status():
    """Check current gate status"""
    try:
        # Gate status is stored in a file on the host
        result = subprocess.run(['cat', HOSTNAME_FILE], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            hostname = result.stdout.strip()
            return f"Gate Status: {GATE_STATUS}\nHost System: {hostname}\nCode Location: {GATE_CODE}"
    except:
        pass
    return f"Gate Status: {GATE_STATUS}\nCode Location: {GATE_CODE}"

def handle_command(command, client_socket):
    """Handle SCADA commands"""
    global GATE_STATUS
    
    cmd = command.strip().lower()
    
    if cmd == "help" or cmd == "?":
        return """
╔══════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                    ║
╚══════════════════════════════════════════════════════════╝

  status          - Display gate status and system info
  unlock <code>   - Unlock the gate with authorization code
  lock            - Lock the gate
  info            - Display system information
  clear           - Clear terminal screen
  exit            - Disconnect from SCADA terminal
  
╔══════════════════════════════════════════════════════════╗
║  NOTE: Gate unlock requires host system authorization    ║
║        Access host filesystem to retrieve unlock code    ║
╚══════════════════════════════════════════════════════════╝
"""
    
    elif cmd == "status":
        return get_gate_status()
    
    elif cmd == "info":
        info = """
╔══════════════════════════════════════════════════════════╗
║                  SYSTEM INFORMATION                      ║
╚══════════════════════════════════════════════════════════╝
"""
        try:
            # Container info
            with open('/proc/self/cgroup', 'r') as f:
                cgroup = f.read()
            info += f"CGroup: {cgroup[:100]}...\n"
            
            # Check if privileged
            try:
                with open('/proc/self/status', 'r') as f:
                    status = f.read()
                    if 'CapEff:' in status:
                        info += "Container Capabilities: Detected\n"
            except:
                pass
                
        except Exception as e:
            info += f"Error retrieving info: {str(e)}\n"
        
        info += "\n[!] System running in containerized environment"
        info += "\n[!] Host access required for gate authorization"
        return info
    
    elif cmd.startswith("unlock "):
        code = command[7:].strip()
        
        # To unlock, need to read the code from the host
        # The real code is in /host/flag on the host filesystem
        # Players need to escape to host to read it
        
        # Check if it's a direct flag submission (starts with THM{)
        if code.startswith("THM{"):
            if "unl0ckth3g4t350fh3ll" in code.lower():
                GATE_STATUS = "UNLOCKED"
                return """
╔══════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════╝

[✓] Authorization code verified
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

FLAG: THM{unl0ckth3g4t350fh3ll}
"""
            else:
                return "[✗] Invalid authorization code."
        
        # Check if it's a file path
        if os.path.exists(code):
            try:
                with open(code, 'r') as f:
                    content = f.read().strip()
                if "THM{" in content and "unl0ckth3g4t350fh3ll" in content.lower():
                    GATE_STATUS = "UNLOCKED"
                    # Extract flag from content
                    flag_start = content.find("THM{")
                    flag_end = content.find("}", flag_start) + 1
                    flag = content[flag_start:flag_end] if flag_start != -1 else content
                    return f"""
╔══════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════╝

[✓] Authorization code verified from: {code}
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

FLAG: {flag}
"""
            except Exception as e:
                return f"[✗] Error reading file: {str(e)}"
        
        return "[✗] Invalid authorization code."
    
    elif cmd == "lock":
        GATE_STATUS = "LOCKED"
        return "[✓] Gate has been locked."
    
    elif cmd == "clear":
        return "\n" * 50
    
    elif cmd == "exit" or cmd == "quit":
        return "[*] Disconnecting from SCADA terminal..."
    
    elif cmd == "":
        return ""
    
    else:
        return f"[✗] Unknown command: {command}\nType 'help' for available commands"

def handle_client(client_socket, addr):
    """Handle client connection"""
    try:
        client_socket.send(BANNER.encode())
        client_socket.send(print_prompt().encode())
        
        while True:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break
            
            response = handle_command(data, client_socket)
            if response is not None:
                client_socket.send(response.encode())
                
                if data.strip().lower() in ["exit", "quit"]:
                    break
                    
                client_socket.send(print_prompt().encode())
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def main():
    """Main server loop"""
    host = '0.0.0.0'
    port = 9001
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[*] SCADA Terminal listening on {host}:{port}")
        print("[*] Waiting for connections...")
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[+] Connection from {addr}")
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, addr)
            )
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[*] Shutting down SCADA terminal...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
