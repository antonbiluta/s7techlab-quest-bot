from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет\\! Я распределительная шляпа\\. Введи кодовое слово из своего предсказания\\.\n\n"
        "||Это которое у тебя __подчеркнуто__||",
        parse_mode=ParseMode.MARKDOWN_V2)
