from aiogram import Router
from handlers.admin.base import router as base
from handlers.admin.teams_command import router as chat_info_command
from handlers.admin.notify_command import router as notify_command

router = Router()
router.include_routers(base, chat_info_command, notify_command)
