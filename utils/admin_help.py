from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat


async def set_admin_commands(bot: Bot, admin_chat_id: int):
    """
    Устанавливает команды бота для чата администраторов.
    """
    admin_commands = [
        BotCommand(command="notify", description="Отправить сообщение командам"),
        BotCommand(command="teams", description="Показать информацию о командах"),
        BotCommand(command="reset_team", description="Сбросить команду пользователю"),
        # BotCommand(command="help", description="Показать помощь"),
    ]
    await bot.set_my_commands(commands=admin_commands, scope=BotCommandScopeChat(chat_id=admin_chat_id))
