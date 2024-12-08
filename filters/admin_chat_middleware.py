from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AdminChatMiddleware(BaseMiddleware):
    def __init__(self, admin_chat_id: int):
        super().__init__()
        self.admin_chat_id = admin_chat_id

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["admin_chat_id"] = self.admin_chat_id
        return await handler(event, data)
