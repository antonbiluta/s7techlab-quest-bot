import asyncio
from typing import List

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.enums.chat_action import ChatAction

from data.crud import team as team_repository
from data.models.team import TeamChat
from utils.constants import START_QUEST_CALLBACK
from utils.sender import sender_to_group
from utils.texts import quest_part_one


router = Router()


@router.message(Command("quest_test"))
async def quest_test(message: Message):
    teams = await team_repository.get_all_teams()
    quest_message = {
        "text": "Квест начинается! Все готовы? 🚀",
        "interval": "5"
    }
    await send_for_all(teams, message.bot, quest_message)
    await func_quest(teams, message.bot)


@router.callback_query(lambda c: c.data == START_QUEST_CALLBACK)
async def start_quest(callback_query: CallbackQuery):
    quest_message = {
        "text": "Квест начинается! Все готовы? 🚀"
    }
    teams = await team_repository.get_all_teams()
    await send_for_all(teams, callback_query.bot, quest_message)
    await callback_query.message.edit_text("Квест начат! Сообщение отправлено во все командные чаты.")
    await callback_query.answer("Квест начат!")
    await func_quest(teams, callback_query.bot)


async def func_quest(teams, bot: Bot):
    for msg in quest_part_one:
        await send_for_all(teams, bot, msg)


async def send_for_all(teams: List[TeamChat], bot: Bot, quest_message: dict):
    interval = quest_message.get('interval', 0)
    quest_text = quest_message.get('text')

    async def send_to_chat(chat_id: int, text: str):
        typing_delay = len(text) * 0.05
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(typing_delay)
        await sender_to_group(bot, chat_id, text)

    tasks = []
    for team in teams:
        tasks.append(send_to_chat(team.group_id, quest_text))

    await asyncio.gather(*tasks)
    await asyncio.sleep(interval)
