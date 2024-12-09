from aiogram import Router
from aiogram.types import Message

from data.crud import user as user_repository
from data.crud import team as team_repository
from data.models.team import TeamChat
from data.utils.functions import is_not_exist
from utils.validators import chat_type_is_private, is_service_message

router = Router()


@router.message()
async def handle_keyword(message: Message, config: dict):
    if is_service_message(message):
        return
    existing_team = await user_repository.get_user_team(user_id=message.from_user.id)
    if is_not_exist(existing_team) and chat_type_is_private(message):
        await check_user_team(message, config)
        return

    print(f"{message.chat.full_name} - {message.chat.type} - {message.chat.id}")
    # await message.answer("Не понял...")


async def check_user_team(message: Message, config: dict):
    teams: dict = config["quest"]["parameters"].get("teams_info", dict())
    keyword = message.text.strip().lower()

    for team_name, data in teams.items():
        if keyword == data["keyword"]:
            team = await team_repository.get_team_by_name(team_name)
            if not team:
                await message.answer(f"Чат команды {team_name.capitalize()} не настроен.")
                return
            if team.is_complete():
                await message.answer(f"Команда уже укомплектована. Обратитесь к администратору.")
                return

            await message.answer(f"Опа, это слово нам подходит. Присоединяйся к чату своей команды: {team.invite_link}")
            await notify_admin_group(team, message, config)
            return

    print(f"{message.chat.full_name} - {message.chat.type} - {message.chat.id}")
    await message.answer("Неизвестное кодовое слово. Попробуйте еще раз.")


async def notify_admin_group(team: TeamChat, message: Message, config: dict):
    admin_group_id: int = config["bot"]["parameters"].get("admin_group_id", list())
    user_id = message.from_user.id
    username = message.from_user.username
    admin_message = (
        f"Выдал ссылку на приглашение в команду {team.name.capitalize()} "
        f"пользователю <a href='tg://user?id={user_id}'>{username or 'пользователь'}</a>."
    )
    await message.bot.send_message(admin_group_id, admin_message, parse_mode="HTML")
