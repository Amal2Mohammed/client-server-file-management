"""
Server for a simple client-server file management protocol.

Supported commands:
LIST <path>
MKDIR <path>
DOWNLOAD <path>
UPLOAD <destination_path> <byte_length>
DELETE <path>
EXIT

Run:
    python server.py 9999
"""

import os
import socket
import sys
from pathlib import Path

BUFFER_SIZE = 4096
HOST = "localhost"

STATUS_OK = 200
STATUS_NOT_FOUND = 404
STATUS_ALREADY_EXISTS = 409
STATUS_BAD_REQUEST = 400
STATUS_ERROR = 500


def safe_path(path: str) -> Path:
    """Convert user path to a local server path."""
    if path == "/":
        return Path.cwd()
    return Path(path)


def send_line(conn: socket.socket, line: str) -> None:
    conn.sendall((line + "\n").encode("utf-8"))


def recv_line(conn: socket.socket) -> str:
    data = bytearray()
    while True:
        chunk = conn.recv(1)
        if not chunk:
            break
        if chunk == b"\n":
            break
        data.extend(chunk)
    return data.decode("utf-8")


def recv_exact(conn: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = conn.recv(min(BUFFER_SIZE, size - len(data)))
        if not chunk:
            raise ConnectionError("Connection closed before receiving full file content.")
        data.extend(chunk)
    return bytes(data)


def handle_client(conn: socket.socket) -> None:
    with conn:
        while True:
            try:
                request = recv_line(conn).strip()
                if not request:
                    break

                parts = request.split(" ", 2)
                command = parts[0].upper()

                if command == "LIST":
                    path = parts[1] if len(parts) > 1 else "/"
                    directory = safe_path(path)

                    if not directory.exists() or not directory.is_dir():
                        send_line(conn, f"{STATUS_NOT_FOUND} Directory not found")
                        continue

                    items = os.listdir(directory)
                    send_line(conn, f"{STATUS_OK} {len(items)} item(s)")
                    send_line(conn, "\n".join(items) if items else "(empty)")

                elif command == "MKDIR":
                    if len(parts) < 2:
                        send_line(conn, f"{STATUS_BAD_REQUEST} Missing directory path")
                        continue

                    directory = safe_path(parts[1])
                    if directory.exists():
                        send_line(conn, f"{STATUS_ALREADY_EXISTS} Directory already exists")
                    else:
                        directory.mkdir(parents=True)
                        send_line(conn, f"{STATUS_OK} Directory created")

                elif command == "DOWNLOAD":
                    if len(parts) < 2:
                        send_line(conn, f"{STATUS_BAD_REQUEST} Missing file path")
                        continue

                    file_path = safe_path(parts[1])
                    if not file_path.exists() or not file_path.is_file():
                        send_line(conn, f"{STATUS_NOT_FOUND} File not found")
                        continue

                    content = file_path.read_bytes()
                    send_line(conn, f"{STATUS_OK} {len(content)}")
                    conn.sendall(content)

                elif command == "UPLOAD":
                    if len(parts) < 3:
                        send_line(conn, f"{STATUS_BAD_REQUEST} Usage: UPLOAD <destination_path> <byte_length>")
                        continue

                    dest_path = safe_path(parts[1])
                    try:
                        content_size = int(parts[2])
                    except ValueError:
                        send_line(conn, f"{STATUS_BAD_REQUEST} Invalid file size")
                        continue

                    send_line(conn, f"{STATUS_OK} Ready")
                    content = recv_exact(conn, content_size)

                    if dest_path.parent:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)

                    dest_path.write_bytes(content)
                    send_line(conn, f"{STATUS_OK} File uploaded")

                elif command == "DELETE":
                    if len(parts) < 2:
                        send_line(conn, f"{STATUS_BAD_REQUEST} Missing file path")
                        continue

                    file_path = safe_path(parts[1])
                    if not file_path.exists() or not file_path.is_file():
                        send_line(conn, f"{STATUS_NOT_FOUND} File not found")
                    else:
                        file_path.unlink()
                        send_line(conn, f"{STATUS_OK} File deleted")

                elif command == "EXIT":
                    send_line(conn, f"{STATUS_OK} Connection closed")
                    break

                else:
                    send_line(conn, f"{STATUS_BAD_REQUEST} Unknown command")

            except Exception as error:
                send_line(conn, f"{STATUS_ERROR} {error}")


def start_server(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, port))
        server.listen(5)

        print(f"Server running on {HOST}:{port}")

        while True:
            conn, addr = server.accept()
            print(f"Client connected: {addr}")
            handle_client(conn)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    start_server(int(sys.argv[1]))
