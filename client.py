"""
Client for a simple client-server file management protocol.

Run:
    python client.py localhost 9999
"""

import socket
import sys
from pathlib import Path

BUFFER_SIZE = 4096


def send_line(sock: socket.socket, line: str) -> None:
    sock.sendall((line + "\n").encode("utf-8"))


def recv_line(sock: socket.socket) -> str:
    data = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            break
        if chunk == b"\n":
            break
        data.extend(chunk)
    return data.decode("utf-8")


def recv_exact(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(min(BUFFER_SIZE, size - len(data)))
        if not chunk:
            raise ConnectionError("Connection closed before receiving full file content.")
        data.extend(chunk)
    return bytes(data)


def print_status(line: str) -> int:
    parts = line.split(" ", 1)
    status = int(parts[0])
    message = parts[1] if len(parts) > 1 else ""

    readable = {
        200: "Success",
        400: "Bad request",
        404: "File or directory not found",
        409: "Already exists",
        500: "Server error",
    }

    print(f"{readable.get(status, 'Response')}: {message}")
    return status


def send_request(sock: socket.socket) -> bool:
    print("\nWhat would you like to do?")
    print("1- list")
    print("2- download")
    print("3- upload")
    print("4- delete")
    print("5- make directory")
    print("6- exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        path = input("Enter server path (/ for current directory): ").strip()
        send_line(sock, f"LIST {path}")
        status = print_status(recv_line(sock))
        if status == 200:
            print(recv_line(sock))

    elif choice == "2":
        server_file = input("Enter server file path to download: ").strip()
        local_file = input("Enter local destination file name: ").strip()
        send_line(sock, f"DOWNLOAD {server_file}")

        response = recv_line(sock)
        status = print_status(response)
        if status == 200:
            size = int(response.split(" ", 1)[1])
            content = recv_exact(sock, size)
            Path(local_file).write_bytes(content)
            print(f"Downloaded to {local_file}")

    elif choice == "3":
        local_file = input("Enter local file path to upload: ").strip()
        server_destination = input("Enter destination path on server: ").strip()

        content = Path(local_file).read_bytes()
        send_line(sock, f"UPLOAD {server_destination} {len(content)}")

        status = print_status(recv_line(sock))
        if status == 200:
            sock.sendall(content)
            print_status(recv_line(sock))

    elif choice == "4":
        server_file = input("Enter server file path to delete: ").strip()
        send_line(sock, f"DELETE {server_file}")
        print_status(recv_line(sock))

    elif choice == "5":
        directory = input("Enter directory path to create: ").strip()
        send_line(sock, f"MKDIR {directory}")
        print_status(recv_line(sock))

    elif choice == "6":
        send_line(sock, "EXIT")
        print_status(recv_line(sock))
        return False

    else:
        print("Invalid choice.")

    return True


def run_client(host: str, port: int) -> None:
    connection_type = input("Choose connection type:\n1- Persistent\n2- Non-persistent\n").strip()

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))

            keep_running = send_request(sock)

            if not keep_running:
                break

            if connection_type == "1":
                while send_request(sock):
                    pass
                break

            if connection_type == "2":
                another = input("Send another request? y/n: ").strip().lower()
                if another != "y":
                    break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    run_client(sys.argv[1], int(sys.argv[2]))
