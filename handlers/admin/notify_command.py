from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.crud import team as team_repository
from data.models.team import TeamChat

router = Router()

user_selections = {}


def create_keyboard_with_selected_teams(user_data: dict, teams: List[TeamChat]) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    for team in teams:
        selected = ""
        if user_data.items():
            selected = "✅" if team.group_id in user_data["selected_teams"] else ""
        keyboard.button(text=f"{selected} {team.name}", callback_data=f"select_team:{team.group_id}")
    keyboard.button(text="Отметить всех", callback_data="notify_select_all")
    keyboard.button(text="Отправить", callback_data="notify_send_message")
    keyboard.button(text="Отмена ❌", callback_data="cancel")
    keyboard.adjust(1)
    return keyboard


@router.message(Command("notify"))
async def notify(message: Message):
    if not message.reply_to_message:
        await message.reply("Команда /notify должна быть ответом на сообщение.")
        return
    user_selections[message.from_user.id] = {
        "original_message": message.reply_to_message,
        "selected_teams": []
    }
    teams = await team_repository.get_all_teams()
    keyboard = create_keyboard_with_selected_teams(user_data=dict(), teams=teams)
    await message.reply("Выберите команды для отправки сообщения:", reply_markup=keyboard.as_markup())


@router.callback_query(lambda callback: callback.data.startswith("select_team:"))
async def select_team(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_selections:
        await callback.message.reply("Сессия истекла. Введите /notify снова.")
        return
    chat_id = int(callback.data.split(":")[1])
    user_data = user_selections[user_id]
    if chat_id in user_data["selected_teams"]:
        user_data["selected_teams"].remove(chat_id)
    else:
        user_data["selected_teams"].append(chat_id)
    teams = await team_repository.get_all_teams()
    keyboard = create_keyboard_with_selected_teams(user_data, teams)
    await callback.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@router.callback_query(lambda callback: callback.data == "notify_select_all")
async def select_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_selections:
        await callback.message.reply("Сессия истекла. Введите /notify снова.")
        return
    user_data = user_selections[user_id]
    teams = await team_repository.get_all_teams()
    if len(user_data["selected_teams"]) == len(teams):
        user_data["selected_teams"].clear()
    else:
        user_data["selected_teams"] = [team[2] for team in teams]
    keyboard = create_keyboard_with_selected_teams(user_data, teams)
    await callback.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@router.callback_query(lambda callback: callback.data == "notify_send_message")
async def send_message(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_selections:
        await callback.message.reply("Сессия истекла. Введите /notify снова.")
        return
    user_data = user_selections[user_id]
    selected_teams = user_data["selected_teams"]
    if not selected_teams:
        await callback.answer("Вы не выбрали ни одной команды!", show_alert=True)
        return
    original_message = user_data["original_message"]
    for chat_id in selected_teams:
        await original_message.copy_to(chat_id)
    del user_selections[user_id]
    await callback.message.edit_text("Сообщение успешно отправлено!")
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "notify_cancel")
async def cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_selections:
        del user_selections[user_id]
    await callback.message.edit_text("Операция отменена.")
    await callback.answer()
