from __future__ import annotations

from datetime import UTC, datetime

from flask import current_app, redirect, render_template, request, session, url_for

from auth import login, protect
from file_store import append_note_to_html
from intel_processor import process_intel
from models import MissionStatusPoll, db
from registry import MissionRoute
from vault_manager import CreditManager


def login_page():
    error = ""
    if request.method == "POST":
        if login(request.form.get("username", ""), request.form.get("password", "")):
            return_url = request.args.get("next") or "/two"
            return redirect(return_url)
        error = "Invalid demo credentials."
    return render_template("login.html", error=error)


def mission_one():
    system_info = {
        "status": "OPERATIONAL",
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "active_region": "EU-Central",
        "ss": current_app.config.get("SECRET_KEY"),
        "dd": current_app.config.get("SQLALCHEMY_DATABASE_URI"),
    }
    return render_template("mission.html", mission="One", mode="public", system_info=system_info)

@protect()
def mission_two():
    note_saved = False
    if request.method == "POST":
        note = request.form.get("note", "").strip()
        if note:
            append_note_to_html(session["username"], note)
            note_saved = True

    return render_template(
        "mission.html",
        mission="Two",
        mode="authenticated",
        username=session["username"],
        browser_agent=request.headers.get("User-Agent", "unknown"),
        note_saved=note_saved,
    )


def mission_three():
    return render_template(
        "mission.html",
        mission="Three",
        mode="operator authorized",
        username=session["username"],
        websocket_url="/three/poll",
    )


@protect()
def mission_four():
    intel_saved = False
    if request.method == "POST":
        intel = request.form.get("intel", "").strip()
        if intel:
            process_intel(session["username"], intel)
            intel_saved = True

    return render_template(
        "mission.html",
        mission="Four",
        mode="authenticated",
        username=session["username"],
        intel_saved=intel_saved,
    )


@protect()
def mission_five():
    transfer_complete = False
    error = ""
    if request.method == "POST":
        target_agent = request.form.get("target_agent", "").strip()
        credits_str = request.form.get("credits", "").strip()
        if target_agent and credits_str.isdigit():
            amount = int(credits_str)
            if CreditManager.transfer_credits(session["username"], target_agent, amount):
                transfer_complete = True
            else:
                error = "Insufficient credits or invalid amount."

    return render_template(
        "mission.html",
        mission="Five",
        mode="authenticated",
        username=session["username"],
        transfer_complete=transfer_complete,
        error=error,
    )


def poll_mission_status(ws, *, username: str) -> None:
    while True:
        message = ws.receive()
        if message is None:
            return

        poll = MissionStatusPoll(username=username, message=message[:120])
        db.session.add(poll)
        db.session.commit()
        ws.send(f"mission-status:{datetime.now(UTC).isoformat()}")


MISSION_ROUTES = [
    MissionRoute("/one", "one", mission_one),
    MissionRoute("/two", "two", mission_two),
    MissionRoute(
        "/three",
        "three",
        mission_three,
        dynamic_protection=True,
        role="operator",
        websocket_handler=poll_mission_status,
    ),
    MissionRoute("/four", "four", mission_four),
    MissionRoute("/five", "five", mission_five),
]
