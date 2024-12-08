async def sender_to_group(callback_query, chat_id, message):
    try:
        await callback_query.bot.send_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в чат {chat_id}: {e}")