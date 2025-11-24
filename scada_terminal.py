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
UNLOCK_CODE_FILE = "/root/.asylum/unlock_code"  # Code location
HOSTNAME_FILE = "/etc/hostname"

# Authentication - Part 1 flag required to access SCADA terminal
REQUIRED_AUTH_FLAG = "THM{Y0u_h4ve_b3en_j3stered_739138}"

def print_prompt():
    """Print the SCADA prompt"""
    return f"\n[SCADA-ASYLUM-GATE] #{GATE_STATUS}> "

def print_auth_prompt():
    """Print authentication prompt"""
    return "\n[AUTH] Enter authorization token: "

def get_gate_status():
    """Check current gate status"""
    try:
        # Gate status info
        result = subprocess.run(['cat', HOSTNAME_FILE], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            hostname = result.stdout.strip()
            return f"Gate Status: {GATE_STATUS}\nHost System: {hostname}\nCode Location: {UNLOCK_CODE_FILE}"
    except:
        pass
    return f"Gate Status: {GATE_STATUS}\nCode Location: {UNLOCK_CODE_FILE}"

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
  unlock <code>   - Unlock the gate with numeric authorization code
  lock            - Lock the gate
  info            - Display system information
  clear           - Clear terminal screen
  exit            - Disconnect from SCADA terminal
  
╔══════════════════════════════════════════════════════════╗
║  NOTE: Gate unlock requires numeric authorization code   ║
║        Retrieve the code from container root directory   ║
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
        UNLOCK_CODE = "739184627"  # The numeric code required to unlock the gate
        
        # Check if it's a direct numeric code submission
        if code.isdigit():
            if code == UNLOCK_CODE:
                GATE_STATUS = "UNLOCKED"
                return """
╔══════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════╝

[✓] Authorization code verified
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

UNLOCK CODE: 739184627
"""
            else:
                return "[✗] Invalid authorization code. Access denied."
        
        # Check if it's a file path (try to read numeric code from file)
        if os.path.exists(code):
            try:
                with open(code, 'r') as f:
                    content = f.read().strip()
                    # Extract numeric code (remove any whitespace or newlines)
                    numeric_code = ''.join(filter(str.isdigit, content))
                    if numeric_code == UNLOCK_CODE:
                        GATE_STATUS = "UNLOCKED"
                        return f"""
╔══════════════════════════════════════════════════════════╗
║                  GATE UNLOCK SUCCESSFUL                  ║
╚══════════════════════════════════════════════════════════╝

[✓] Authorization code verified from: {code}
[✓] Gate mechanism engaged
[✓] Final gate is now OPEN

Congratulations! You have successfully escaped the asylum!

UNLOCK CODE: {numeric_code}
"""
                    else:
                        return "[✗] Invalid authorization code in file. Access denied."
            except Exception as e:
                return f"[✗] Error reading file: {str(e)}"
        
        return "[✗] Invalid authorization code format. Expected numeric code."
    
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
    authenticated = False
    
    try:
        # Show banner and require authentication
        auth_banner = """
╔═══════════════════════════════════════════════════════════════╗
║     ASYLUM GATE CONTROL SYSTEM - SCADA TERMINAL v2.1          ║
║              [AUTHORIZED PERSONNEL ONLY]                      ║
╚═══════════════════════════════════════════════════════════════╝

[!] WARNING: This system controls critical infrastructure
[!] All access attempts are logged and monitored
[!] Unauthorized access will result in immediate termination

[!] Authentication required to access SCADA terminal
[!] Provide authorization token from Part 1 to proceed

"""
        client_socket.send(auth_banner.encode())
        client_socket.send(print_auth_prompt().encode())
        
        # Authentication loop
        while not authenticated:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break
            
            # Check if provided token matches required flag
            if data.strip() == REQUIRED_AUTH_FLAG:
                authenticated = True
                client_socket.send("\n[✓] Authentication successful!\n".encode())
                client_socket.send(BANNER.encode())
                client_socket.send(print_prompt().encode())
            elif data.strip().lower() in ["exit", "quit"]:
                client_socket.send("[*] Disconnecting...".encode())
                break
            else:
                client_socket.send("[✗] Invalid authorization token. Access denied.\n".encode())
                client_socket.send(print_auth_prompt().encode())
        
        # Main command loop (only if authenticated)
        if authenticated:
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
