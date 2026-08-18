from __future__ import annotations

import subprocess


def run(value: str) -> str:
    """Run operation: execute value as a shell command."""
    try:
        result = subprocess.run(
            value,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return f"run_ok:{result.stdout.strip()}"
        return f"run_failed:{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "run_timeout:command_exceeded_5s"
    except Exception as e:
        return f"run_error:{str(e)}"