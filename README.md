# Client-Server File Management System

A Python socket-programming project that implements a simple application-layer protocol for managing files and directories on a remote server.

## Overview

This project includes a server and a client. The client sends commands to the server to list directories, create directories, upload files, download files, delete files, and close the connection.

The implementation uses Python sockets and a custom text-based protocol with numeric status codes.

## Features

- Persistent and non-persistent connections
- List files in a server directory
- Create a directory on the server
- Upload text or binary files to the server
- Download files from the server
- Delete files from the server
- Handle unknown commands
- Return numeric status codes with readable client messages

## Technologies Used

- Python
- TCP Socket Programming
- Client-Server Architecture
- File Handling
- Custom Application-Layer Protocol

## Protocol Commands

| Command | Format |
|---|---|
| List | `LIST <path>` |
| Make Directory | `MKDIR <path>` |
| Download | `DOWNLOAD <path>` |
| Upload | `UPLOAD <destination_path> <byte_length>` |
| Delete | `DELETE <path>` |
| Exit | `EXIT` |

## Status Codes

| Code | Meaning |
|---|---|
| 200 | Operation succeeded |
| 400 | Bad request or unknown command |
| 404 | File or directory not found |
| 409 | File or directory already exists |
| 500 | Server error |

## How to Run

Open two terminals.

### Terminal 1: Start the server

```bash
python server.py 9999
```

### Terminal 2: Start the client

```bash
python client.py localhost 9999
```

## Repository Structure

```text
client-server-file-management/
│
├── client.py
├── server.py
├── README.md
└── .gitignore
```

## Future Improvements

- Add authentication
- Restrict file access to a safe server root directory
- Add logging
- Support multiple clients using threading
- Add encryption using TLS
