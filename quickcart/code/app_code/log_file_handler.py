import fcntl
import json
import os
import re
import stat

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


_LOG_DIR = Path(
    os.environ.get(
        "QUICKCART_LOG_DIR",
        "/tmp/quickcart-logs",
    )
)

_LOG_FILE = _LOG_DIR / "errors.log"
_LOCK_FILE = _LOG_DIR / ".errors.lock"

_MAX_ENTRY_LENGTH = 2_000
_MAX_READ_LINES = 200
_MAX_LOG_BYTES = 5 * 1024 * 1024
_ROTATED_LOGS = 3


_REDACTIONS = (
    re.compile(
        r"(?i)(authorization\s*[:=]\s*)([^\s,;]+)"
    ),
    re.compile(
        r"(?i)((?:password|passwd|secret|token|"
        r"api[_-]?key|cookie)\s*[:=]\s*)([^\s,;]+)"
    ),
)


def _secure_dir() -> None:

    try:
        st = os.lstat(_LOG_DIR)

        if stat.S_ISLNK(st.st_mode):
            raise RuntimeError("Unsafe log directory")

        if not stat.S_ISDIR(st.st_mode):
            raise RuntimeError("Unsafe log directory")

        if st.st_uid != os.geteuid():
            raise RuntimeError(
                "Log directory is not owned by application user"
            )

    except FileNotFoundError:

        _LOG_DIR.mkdir(
            mode=0o700,
            parents=True,
            exist_ok=False,
        )

    os.chmod(_LOG_DIR, 0o700)


def _open_fixed_file(
    path: Path,
    flags: int,
    mode: int = 0o600,
) -> int:

    _secure_dir()

    safe_flags = flags | os.O_CLOEXEC

    if hasattr(os, "O_NOFOLLOW"):
        safe_flags |= os.O_NOFOLLOW

    fd = os.open(
        path,
        safe_flags,
        mode,
    )

    try:
        st = os.fstat(fd)

        if not stat.S_ISREG(st.st_mode):
            raise RuntimeError(
                "Unsafe log file type"
            )

        if st.st_uid != os.geteuid():
            raise RuntimeError(
                "Log file is not owned by application user"
            )

        os.fchmod(fd, mode)

        return fd

    except Exception:
        os.close(fd)
        raise


@contextmanager
def _process_lock(exclusive: bool):

    fd = _open_fixed_file(
        _LOCK_FILE,
        os.O_RDWR | os.O_CREAT,
    )

    try:
        fcntl.flock(
            fd,
            fcntl.LOCK_EX
            if exclusive
            else fcntl.LOCK_SH,
        )

        yield

    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _redact(value: str) -> str:

    clean = (
        value
        .replace("\x00", "")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )

    for pattern in _REDACTIONS:
        clean = pattern.sub(
            r"\1[REDACTED]",
            clean,
        )

    return clean[:_MAX_ENTRY_LENGTH]


def _rotate_if_needed() -> None:

    try:
        st = os.lstat(_LOG_FILE)

    except FileNotFoundError:
        return

    if stat.S_ISLNK(st.st_mode):
        raise RuntimeError("Unsafe log file")

    if not stat.S_ISREG(st.st_mode):
        raise RuntimeError("Unsafe log file")

    if st.st_size < _MAX_LOG_BYTES:
        return

    oldest = (
        _LOG_DIR /
        f"errors.log.{_ROTATED_LOGS}"
    )

    try:
        oldest.unlink()
    except FileNotFoundError:
        pass

    for index in range(
        _ROTATED_LOGS - 1,
        0,
        -1,
    ):

        source = (
            _LOG_DIR /
            f"errors.log.{index}"
        )

        target = (
            _LOG_DIR /
            f"errors.log.{index + 1}"
        )

        try:
            source_st = os.lstat(source)

        except FileNotFoundError:
            continue

        if stat.S_ISLNK(source_st.st_mode):
            raise RuntimeError(
                "Unsafe rotated log file"
            )

        if not stat.S_ISREG(source_st.st_mode):
            raise RuntimeError(
                "Unsafe rotated log file"
            )

        os.replace(source, target)

    os.replace(
        _LOG_FILE,
        _LOG_DIR / "errors.log.1",
    )


def write_log(error_log: str) -> None:

    if (
        not isinstance(error_log, str)
        or not error_log.strip()
    ):
        raise ValueError(
            "error_log must be a non-empty string"
        )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(timespec="milliseconds"),

        "error": _redact(error_log),
    }

    encoded = (
        json.dumps(
            record,
            ensure_ascii=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")

    with _process_lock(exclusive=True):

        _rotate_if_needed()

        fd = _open_fixed_file(
            _LOG_FILE,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_APPEND,
        )

        try:
            os.write(fd, encoded)
            os.fsync(fd)

        finally:
            os.close(fd)


def read_logs(limit: int = 100) -> list[dict]:

    if not isinstance(limit, int):
        raise ValueError(
            "limit must be an integer"
        )

    limit = max(
        1,
        min(limit, _MAX_READ_LINES),
    )

    with _process_lock(exclusive=False):

        fd = _open_fixed_file(
            _LOG_FILE,
            os.O_RDONLY | os.O_CREAT,
        )

        try:
            with os.fdopen(
                os.dup(fd),
                "r",
                encoding="utf-8",
                errors="replace",
            ) as stream:

                lines = stream.readlines()[-limit:]

        finally:
            os.close(fd)

    records = []

    for line in lines:

        try:
            record = json.loads(line)

        except json.JSONDecodeError:
            continue

        if (
            isinstance(record, dict)
            and set(record).issuperset(
                {"timestamp", "error"}
            )
        ):
            records.append(record)

    return records

def read_last_log() -> dict | None:
    records = read_logs(limit=1)

    if not records:
        return None

    return records[-1]