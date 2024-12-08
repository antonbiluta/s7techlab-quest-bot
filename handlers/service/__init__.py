from aiogram import Router
from handlers.service.bot_reaction import router as bot_reaction
from handlers.service.user_reaction import router as user_reaction

router = Router()
router.include_routers(bot_reaction, user_reaction)
