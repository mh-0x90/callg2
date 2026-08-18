from __future__ import annotations

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def home(_: HttpRequest) -> HttpResponse:
    return redirect("one")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


def mission_one(request: HttpRequest) -> HttpResponse:
    return render(request, "missions/mission.html", {"mission": "One", "mode": "public"})


@login_required
def mission_two(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "missions/mission.html",
        {
            "mission": "Two",
            "mode": "authenticated",
            "browser_agent": request.headers.get("User-Agent", "unknown"),
        },
    )


def mission_three(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "missions/mission.html",
        {"mission": "Three", "mode": "operator authorized", "websocket_url": "/three/poll/"},
    )