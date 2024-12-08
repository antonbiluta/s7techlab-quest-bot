from aiogram import Router
from aiogram.types import Message

from data import db

router = Router()


@router.message()
async def handle_keyword(message: Message, config: dict):
    if message.new_chat_members or message.left_chat_member:
        return
    existing_user = db.get_user(message.from_user.id)
    if not existing_user and message.chat.type == "private":
        await check_user_team(message, config)
        return

    print(f"{message.chat.full_name} - {message.chat.type} - {message.chat.id}")
    # await message.answer("Не понял...")


async def check_user_team(message: Message, config: dict):
    teams: dict = config["quest"]["parameters"].get("teams_info", dict())
    admin_group_id: int = config["bot"]["parameters"].get("admin_group_id", list())

    user_id = message.from_user.id
    keyword = message.text.strip().lower()
    username = message.from_user.username

    for team_name, data in teams.items():
        if keyword == data["keyword"]:

            chat_info = db.get_chat_info_by_name(team_name)
            if not chat_info:
                await message.answer(f"Чат команды {team_name.capitalize()} не настроен.")
                return

            if chat_info[4] == chat_info[5]:
                await message.answer(f"Команда уже укомплектована. Обратитесь к администратору.")
                return

            chat_link = chat_info[3]
            await message.answer(f"Опа, это слово нам подходит. Присоединяйся к чату своей команды: {chat_link}")

            admin_message = (
                f"Выдал ссылку на приглашение в команду {team_name.capitalize()} "
                f"пользователю <a href='tg://user?id={user_id}'>{username or 'пользователь'}</a>."
            )

            await message.bot.send_message(admin_group_id, admin_message, parse_mode="HTML")
            return

    print(f"{message.chat.full_name} - {message.chat.type} - {message.chat.id}")
    await message.answer("Неизвестное кодовое слово. Попробуйте еще раз.")