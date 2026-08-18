from __future__ import annotations

import html
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "agent_notes.html"


def append_note_to_html(username: str, note_text: str) -> None:
    """Appends an agent note as an HTML entry to agent_notes.html."""
    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "<!doctype html>\n<html>\n<head><title>Agent Notes Log</title></head>\n"
            "<body>\n<h1>Agent Notes Log</h1>\n<ul>\n</ul>\n</body>\n</html>\n",
            encoding="utf-8",
        )

    escaped_user = html.escape(username)
    escaped_note = html.escape(note_text)
    entry = f"  <li><strong>{escaped_user}:</strong> {escaped_note}</li>\n"

    content = LOG_FILE.read_text(encoding="utf-8")
    if "</ul>" in content:
        updated = content.replace("</ul>", f"{entry}</ul>", 1)
        LOG_FILE.write_text(updated, encoding="utf-8")
    else:
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(entry)
