from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class Variables(BaseMiddleware):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["config"] = self.config
        return await handler(event, data)
