from __future__ import annotations

from datetime import UTC, datetime

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import MissionStatusPoll
from .security import is_operator


class MissionStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope["user"]
        if not await sync_to_async(is_operator)(user):
            await self.close(code=4403)
            return
        await self.accept()

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        message = (text_data or "")[:120]
        await MissionStatusPoll.objects.acreate(user=self.scope["user"], message=message)
        await self.send(text_data=f"mission-status:{datetime.now(UTC).isoformat()}")