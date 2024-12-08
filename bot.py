import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import validate_token
from aiogram.methods import DeleteWebhook

from filters.admin_chat_middleware import AdminChatMiddleware
from filters.admin_filter import AdminFilter
from filters.variables_middleware import Variables
from handlers.admin import router as admin_router
from handlers.quest import router as quest_router
from handlers.service import router as service_router
from handlers.common import router as common_router

from config import ConfigManager, update_globals

from data.db import initialize_db, add_chat, init_settings
from utils.admin_help import set_admin_commands


def validate(token):
    if not validate_token(token):
        raise ValueError("Некорректный токен бота.")


def run_background_tasks(config_manager):
    asyncio.create_task(config_manager.start_auto_refresh())


async def init_team(config: dict):
    quest = config["quest"]
    quest_parameters = quest["parameters"]
    default_limit = quest_parameters.get("default_limit", 1)
    teams_info = quest_parameters.get("teams_info", dict())
    for team_code, values in teams_info.items():
        chat_id = values['chat_id']
        link = values['link']
        add_chat(team_code, chat_id, default_limit, link)


async def init_new_settings():
    init_settings("get_default_members", False, None)


async def main():
    config_manager = ConfigManager()
    await config_manager.load_config()
    await update_globals(config_manager.config)
    config_manager.add_listener(update_globals)
    run_background_tasks(config_manager)

    config = config_manager.config
    bot = config["bot"]
    bot_parameters = bot["parameters"]
    bot_token = bot.get("token")
    validate(bot_token)

    initialize_db()
    await init_new_settings()

    await init_team(config)

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(Variables(config=config))
    dp.callback_query.middleware(Variables(config=config))
    dp.message.middleware(Variables(config=config))

    admin_group_id = bot_parameters.get("admin_group_id", list())
    admin_router.message.middleware(AdminFilter(allowed_admins=bot_parameters.get("allowed_admins", list()), allowed_channel_id=admin_group_id))
    service_router.message.middleware(AdminChatMiddleware(admin_chat_id=bot_parameters.get("admin_group_id", list())))

    dp.include_router(service_router)
    dp.include_router(admin_router)

    dp.include_router(quest_router)
    dp.include_router(common_router)

    await set_admin_commands(bot, admin_group_id)

    # await bot(DeleteWebhook(drop_pending_updates=True))

    print("Бот запущен. Нажмите Ctrl+C для завершения.")

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
