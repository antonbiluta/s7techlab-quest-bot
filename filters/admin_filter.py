from aiogram import BaseMiddleware
from aiogram.types import Message


class AdminFilter(BaseMiddleware):
    def __init__(self, allowed_channel_id: int, allowed_admins: list[int | str]):
        super().__init__()
        self.allowed_channel_id = allowed_channel_id
        self.allowed_admins = allowed_admins

    async def __call__(self, handler, event: Message, data: dict):
        if event.chat.type == "channel" and event.chat.id == self.allowed_channel_id:
            return await handler(event, data)

        if event.chat.id == self.allowed_channel_id:
            return await handler(event, data)

        if event.chat.type == "private" and (
            event.from_user.id in self.allowed_admins or
            event.from_user.username in self.allowed_admins
        ):
            return await handler(event, data)

        await event.answer("Не понял...")
