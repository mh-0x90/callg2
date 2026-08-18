from __future__ import annotations

from datetime import UTC, datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class MissionStatusPoll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    received_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))


class AgentCredit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=1000)