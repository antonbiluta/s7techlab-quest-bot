from typing import List

from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters.command import Command

from data.crud import team as team_repository
from data.models.team import TeamChat

router = Router()


admin_states = {}


def create_keyboard_with_team(teams: List[TeamChat]) -> InlineKeyboardMarkup:
    keyboards = list()
    for team in teams:
        keyboards.append([
            InlineKeyboardButton(text=f"{team.name} ({team.count_str()})", callback_data=f"edit__{team.name}")
        ])
    keyboards.append([InlineKeyboardButton(text="Отмена ❌", callback_data="chat_info_cancel")])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=keyboards)


@router.message(Command("teams"))
async def show_chat_info(message: Message):
    teams = await team_repository.get_all_teams()
    if not teams:
        await message.answer("Чаты не настроены")
        return
    keyboard = create_keyboard_with_team(teams)
    await message.answer("Выберите чат для изменения:", reply_markup=keyboard)


@router.callback_query(lambda callback: callback.data == "back_to_chats")
async def show_chat_info_callback(callback: CallbackQuery):
    teams = await team_repository.get_all_teams()
    keyboard = create_keyboard_with_team(teams)
    await callback.message.edit_text("Выберите чат для изменения:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("edit__"))
async def edit_chat(callback_query: CallbackQuery):
    team_name = callback_query.data.split("__")[1]
    admin_states[callback_query.from_user.id] = {"team": team_name}  # Сохраняем выбранный чат

    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Изменить ссылку 🔗", callback_data=f"change_link__{team_name}")],
        [InlineKeyboardButton(text="Изменить лимит участников 👥", callback_data=f"change_limit__{team_name}")],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back_to_chats")]
    ])

    await callback_query.message.edit_text(
        f"Вы выбрали чат: {team_name}. Выберите действие:", reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("change_link__"))
async def change_link(callback_query: CallbackQuery):
    team_name = callback_query.data.split("__")[1]
    admin_states[callback_query.from_user.id] = {"team": team_name, "action": "change_link"}

    await callback_query.message.edit_text(
        f"Отправьте новую ссылку для чата {team_name}."
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("change_limit__"))
async def change_limit(callback_query: CallbackQuery):
    team_name = callback_query.data.split("__")[1]
    team = await team_repository.get_team_by_name(team_name)

    admin_states[callback_query.from_user.id] = {
        "team": team.name,
        "action": "change_limit",
        "original_limit": team.member_limit,
        "current_limit": team.member_limit,
    }

    keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
            InlineKeyboardButton(text="➕", callback_data="limit_increase"),
            InlineKeyboardButton(text="➖", callback_data="limit_decrease"),
            InlineKeyboardButton(text="Reset ↩️", callback_data="limit_reset"),
            InlineKeyboardButton(text="Save ✅", callback_data="limit_save")
        ],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back_to_chats")]
    ])

    await callback_query.message.edit_text(
        f"Текущий лимит для {team.name}: {team.member_limit}\nВыберите действие:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("limit_"))
async def handle_limit_change(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in admin_states or admin_states[user_id].get("action") != "change_limit":
        await callback_query.answer("Не найдено активное изменение лимита.", show_alert=True)
        return

    state = admin_states[user_id]
    if callback_query.data == "limit_increase":
        state["current_limit"] += 1
    elif callback_query.data == "limit_decrease" and state["current_limit"] > 1:
        state["current_limit"] -= 1
    elif callback_query.data == "limit_reset":
        state["current_limit"] = state["original_limit"]
    elif callback_query.data == "limit_save":
        await team_repository.update_limit_by_name(state["team"], state["current_limit"])
        await callback_query.message.edit_text(f"Лимит для {state['team']} сохранен: {state['current_limit']} участников.")
        del admin_states[user_id]
        await callback_query.answer()
        return

    keyboard = callback_query.message.reply_markup
    await callback_query.message.edit_text(
        f"Текущий лимит для {state['team']}: {state['current_limit']}\nВыберите действие:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.message(Command("link"))
async def handle_new_link(message: Message):
    if message.from_user.id not in admin_states or admin_states[message.from_user.id].get("action") != "change_link":
        return

    team_name = admin_states[message.from_user.id]["team"]
    new_link = message.text.strip()

    await team_repository.update_invite_link_by_name(team_name, new_link)

    await message.answer(f"Ссылка для чата {team_name} обновлена!")
    del admin_states[message.from_user.id]


@router.callback_query(lambda callback: callback.data == "chat_info_cancel")
async def cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in admin_states:
        del admin_states[user_id]
    await callback.message.delete()
    await callback.answer()
