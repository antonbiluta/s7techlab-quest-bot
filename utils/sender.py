from aiogram import Bot


async def sender_to_group(bot: Bot, chat_id, message):
    try:
        await bot.send_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в чат {chat_id}: {e}")