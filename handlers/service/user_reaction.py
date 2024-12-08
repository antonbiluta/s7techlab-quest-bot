from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, Command
from aiogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

from data import db
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
    chat_info = db.get_chat_info(chat_id)
    if not chat_info:
        return
    team_name = chat_info[1]
    db.update_members(chat_id, 1)
    db.add_user(user_id, username or "unknown", team_name)
    await message.bot.send_message(user_id, f"Вы успешно добавлены в команду {team_name.capitalize()}!")
    await send_info_about_user_to_admin(message, chat_id, team_name, admin_chat_id)


async def send_info_about_user_to_admin(message: Message, chat_id: int, team_name: str, admin_chat_id: int):
    chat_info = db.get_chat_info(chat_id)
    admin_message = (
        f"Пользователь <a href='tg://user?id={message.from_user.id}'>{message.from_user.username or 'пользователь'}</a> "
        f"вступил в чат команды {team_name.capitalize()} "
        f"({chat_info[4]}/{chat_info[5]} человек)."
    )
    await message.bot.send_message(admin_chat_id, admin_message, parse_mode="HTML")

    if (chat_info[4]) == chat_info[5]:
        await message.bot.send_message(
            admin_chat_id,
            f"Команда {team_name.capitalize()} укомплектована ({chat_info[5]}/{chat_info[5]}).",
            parse_mode="HTML"
        )

    all_chats = db.get_all_chats()
    if all(all_chat[4] == all_chat[5] for all_chat in all_chats):
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
