from __future__ import annotations

import socket


def send_to_relay(value: str) -> str:
    with socket.create_connection(("127.0.0.1", 9099), timeout=3) as relay:
        relay.sendall(value.encode("utf-8"))
        return relay.recv(1024).decode("utf-8")