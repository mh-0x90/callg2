from __future__ import annotations

from flask import Flask, redirect, url_for
from flask_sock import Sock

from auth import logout
from models import db
from registry import register_mission_routes
from routes import MISSION_ROUTES, login_page
from service_plugins import register_service_plugins


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "mission-relay-demo-only"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mission_relay.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    register_service_plugins(app)
    db.init_app(app)
    sock = Sock(app)

    app.add_url_rule("/login", "login", login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", "logout", logout, methods=["POST"])
    app.add_url_rule("/", "home", lambda: redirect(url_for("one")))
    register_mission_routes(app, sock, MISSION_ROUTES)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
