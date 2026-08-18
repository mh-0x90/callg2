from __future__ import annotations

import socket


def main() -> None:
    with socket.create_server(("127.0.0.1", 9099), reuse_port=False) as server:
        print("Demo relay listening on 127.0.0.1:9099")
        while True:
            connection, _ = server.accept()
            with connection:
                value = connection.recv(1024).decode("utf-8")
                connection.sendall(f"relay-received:{value}".encode("utf-8"))


if __name__ == "__main__":
    main()