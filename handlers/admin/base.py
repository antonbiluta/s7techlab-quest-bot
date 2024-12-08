import re

from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from data import db


router = Router()


@router.message(Command("reset_team"))
async def reset_team(message: Message):
    user_id = None
    username = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.text.split(maxsplit=1)) > 1:
        argument = message.text.split(maxsplit=1)[1].strip()
        if argument.startswith("@"):
            username = argument[1:]  # Убираем @
        if argument.isdigit():
            user_id = int(argument)
        if re.match(r"^[a-zA-Z0-9_]+$", argument):
            username = argument
    else:
        await message.answer("Пришлите `/reset_team <@username | username | user_id>`")

    if not user_id and not username:
        await message.answer("Не удалось определить пользователя. Пришлите `/reset_team <@username | username | user_id>`")
        return

    if user_id:
        user_data = db.get_user(user_id)
    else:
        user_data = db.get_user_by_username(username)
    if not user_data:
        await message.answer("Этот пользователь не состоит в какой-либо команде.")
        return

    db.reset_user(user_id)
    await message.answer(f"Пользователь <a href='tg://user?id={user_id}'>{user_data[1]}</a> успешно сброшен из команды {user_data[2]}.")
