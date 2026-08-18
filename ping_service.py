from __future__ import annotations

import ipaddress
import socket


class PingService:
    """Encapsulates ping-style host validation and resolution."""

    @staticmethod
    def _is_ip_address(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _ssh_check(ip_value: str) -> str:
        """Check SSH reachability by testing TCP connectivity on port 22."""
        try:
            with socket.create_connection((ip_value, 22), timeout=3):
                return f"ssh_ok:{ip_value}"
        except TimeoutError:
            return f"ssh_failed:{ip_value}_timeout"
        except OSError:
            return f"ssh_failed:{ip_value}_unreachable"
        except Exception as e:
            return f"ssh_error:{str(e)}"

    @staticmethod
    def ping(value: str) -> str:
        """Route IPs to SSH check, and domains to ping-style resolution."""
        normalized = value.strip()
        if not normalized:
            return "ping_failed:empty_value"

        if PingService._is_ip_address(normalized):
            return PingService._ssh_check(normalized)

        try:
            socket.gethostbyname(normalized)
            return f"ping_ok:{normalized}"
        except socket.gaierror:
            return f"ping_failed:{normalized}_not_reachable"
        except Exception as e:
            return f"ping_error:{str(e)}"
