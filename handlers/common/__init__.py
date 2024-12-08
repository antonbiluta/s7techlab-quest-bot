from aiogram import Router
from handlers.common.start import router as start_command
from handlers.common.any_message import router as any_message_handler

router = Router()
router.include_routers(start_command, any_message_handler)
