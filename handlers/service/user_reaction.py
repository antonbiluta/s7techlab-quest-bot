from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, Command
from aiogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

from data.crud import user as user_repository
from data.crud import team as team_repository
from data.models.team import TeamChat
from utils.constants import START_QUEST_CALLBACK

router = Router()


@router.message(Command("test_join"))
async def test_join(message: Message, admin_chat_id: int):
    await on_user_join(message, message.chat.id, message.from_user.id, message.from_user.username, admin_chat_id)


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_user_join_event(event: ChatMemberUpdated, config: dict):
    admin_chat_id = config["bot"]["parameters"]["admin_group_id"]
    chat_id = event.chat.id
    user_id = event.new_chat_member.user.id
    username = event.new_chat_member.user.username

    await on_user_join(event, chat_id, user_id, username, admin_chat_id)


async def on_user_join(message: [Message, ChatMemberUpdated], chat_id, user_id, username, admin_chat_id: int):
    team = await team_repository.get_team(chat_id)
    if not team:
        return
    team_id = await user_repository.get_user_team(user_id)
    if team_id:
        return
    if not team.validate_increment():
        return
    await user_repository.create_or_update_user(user_id=user_id, username=username or "unknown", team_id=team.id)
    await team_repository.update_members(chat_id, 1)
    await message.bot.send_message(user_id, f"Вы успешно добавлены в команду {team.name.capitalize()}!")
    team = await team_repository.get_team(chat_id)
    await send_info_about_user_to_admin(message, team, admin_chat_id)


async def send_info_about_user_to_admin(message: Message, team: TeamChat, admin_chat_id: int):
    admin_message = (
        f"Пользователь <a href='tg://user?id={message.from_user.id}'>{message.from_user.username or 'пользователь'}</a> "
        f"вступил в чат команды {team.name.capitalize()} "
        f"({team.count_str()} человек)."
    )
    await message.bot.send_message(admin_chat_id, admin_message, parse_mode="HTML")

    if team.is_complete():
        await message.bot.send_message(
            admin_chat_id,
            f"Команда {team.name.capitalize()} укомплектована ({team.count_str()}).",
            parse_mode="HTML"
        )

    if await team_repository.are_all_chats_full():
        await notify_all_teams_ready(message.bot, admin_chat_id)


async def notify_all_teams_ready(bot, admin_chat_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать квест", callback_data=START_QUEST_CALLBACK)]
        ]
    )
    await bot.send_message(
        admin_chat_id,
        "Все команды укомплектованы! 🎉\nНажмите на кнопку ниже, чтобы начать квест.",
        reply_markup=keyboard
    )
