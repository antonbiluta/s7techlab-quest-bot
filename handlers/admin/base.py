import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters.command import Command

from data.crud import user as user_repository
from data.crud import team as team_repository


router = Router()


def extract_user(message: Message):
    user_id = None
    username = None
    args = message.text.split(maxsplit=1)
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
    elif len(args) == 2:
        argument = args[1].strip()
        if argument.startswith("@"):
            username = argument[1:]
        if argument.isdigit():
            user_id = int(argument)
        if re.match(r"^[a-zA-Z0-9_]+$", argument):
            username = argument
    return user_id, username


@router.message(Command("reset_team"))
async def reset_team(message: Message):
    user_id, username = extract_user(message)
    if not user_id and not username:
        await message.answer("Не удалось определить пользователя\\. Пришлите `/reset_team <\\@username | username | user_id>`", parse_mode=ParseMode.MARKDOWN_V2)
        return

    user_data = await user_repository.get_user_with_team(user_id=user_id, username=username)

    if not user_data:
        await message.answer("Этот пользователь не состоит в какой-либо команде.")
        return

    await team_repository.update_members(user_data.team.group_id, -1)
    await user_repository.reset_user_team(user_data.id)
    await message.answer(f"Пользователь <a href='tg://user?id={user_data.id}'>{user_data.username}</a> успешно сброшен из команды {user_data.team.name}.")
