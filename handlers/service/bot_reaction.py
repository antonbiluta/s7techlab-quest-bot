from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated


router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_add_bot_to_group(event: ChatMemberUpdated):
    print(event)
    if event.new_chat_member.user.id == event.bot.id:
        chat_title = event.chat.title
        await event.bot.send_message(
            chat_id=event.chat.id,
            text=f"Привет! Я теперь в {chat_title}. Рад быть с вами!"
        )
        print(event.chat.id)
