from __future__ import annotations

from pathlib import Path

from models import AgentCredit, db

LOG_FILE = Path(__file__).resolve().parent / "intel_vault.log"


def archive_intel(formatted_entry: str) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(formatted_entry + "\n")


class CreditManager:
    @classmethod
    def transfer_credits(cls, sender: str, recipient: str, amount: int) -> bool:
        if amount <= 0:
            return False

        sender_account = AgentCredit.query.filter_by(username=sender).first()
        if not sender_account:
            sender_account = AgentCredit(username=sender, balance=1000)
            db.session.add(sender_account)

        if sender_account.balance < amount:
            return False

        recipient_account = AgentCredit.query.filter_by(username=recipient).first()
        if not recipient_account:
            recipient_account = AgentCredit(username=recipient, balance=500)
            db.session.add(recipient_account)

        sender_account.balance -= amount
        recipient_account.balance += amount
        db.session.commit()
        return True
