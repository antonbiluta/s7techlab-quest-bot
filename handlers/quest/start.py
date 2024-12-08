import asyncio
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.enums.chat_action import ChatAction

from data import db
from utils.constants import START_QUEST_CALLBACK
from utils.sender import sender_to_group
from utils.texts import quest_part_one


router = Router()

@router.message(Command("quest_test"))
async def quest_test(message: Message):
    all_chats = db.get_all_chats()
    await func_quest(all_chats, message)

@router.callback_query(lambda c: c.data == START_QUEST_CALLBACK)
async def start_quest(callback_query: CallbackQuery):
    quest_message = "Квест начинается! Все готовы? 🚀"

    all_chats = db.get_all_chats()
    for chat in all_chats:
        chat_id = chat[2]
        try:
            await callback_query.bot.send_message(chat_id, quest_message)
        except Exception as e:
            print(f"Ошибка отправки сообщения в чат {chat_id}: {e}")

    await callback_query.message.edit_text("Квест начат! Сообщение отправлено во все командные чаты.")
    await callback_query.answer("Квест начат!")

    await func_quest(all_chats, callback_query)


async def func_quest(all_chats, callback_query):
    for msg in quest_part_one:
        await send_for_all(all_chats, callback_query, msg)


async def send_for_all(all_chats, callback_query, quest_message: dict):
    interval = quest_message.get('interval')
    quest_text = quest_message.get('text')

    async def send_to_chat(chat_id: int, text: str):
        typing_delay = len(text) * 0.05
        await callback_query.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(typing_delay)
        await sender_to_group(callback_query, chat_id, text)

    tasks = []
    for chat in all_chats:
        tasks.append(send_to_chat(chat[2], quest_text))

    await asyncio.gather(*tasks)
    await asyncio.sleep(interval)
