import socket
import os
import tqdm

# Server configuration
HOST = "0.0.0.0"  # Listen on all network interfaces
PORT = 4444  # Port number
BUFFER_SIZE = 4096  # Data buffer size
SEPARATOR = "<END>"  # End of file marker

def send_file(filename, client_socket):
    """Handles sending a file to the connected client."""
    try:
        file_size = os.path.getsize(filename)  # Get file size
        print(f"[+] Sending '{filename}' ({file_size} bytes)")

        # Send file info to client
        client_socket.send(f"{filename}{SEPARATOR}{file_size}".encode())

        # Wait for client acknowledgment
        client_socket.recv(BUFFER_SIZE)

        # Send the file in chunks
        progress = tqdm.tqdm(unit="B", unit_scale=True, total=file_size, desc="Sending")
        with open(filename, "rb") as file:
            while chunk := file.read(BUFFER_SIZE):  # Read file in chunks
                client_socket.send(chunk)
                progress.update(len(chunk))

        progress.close()
        print("[+] File transfer completed.")

    except Exception as e:
        print(f"[-] Error sending file: {e}")

def start_server():
    """Starts the file transfer server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # Listen for a single connection

    print(f"[*] Server listening on {HOST}:{PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[+] Connection established with {addr}")

        filename = input("[*] Enter the file to send: ")
        if os.path.exists(filename):
            send_file(filename, client_socket)
        else:
            print("[-] File not found.")

        client_socket.close()
        print("[!] Connection closed.")

if __name__ == "__main__":
    start_server()
