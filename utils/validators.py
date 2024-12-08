from aiogram.types import Message


def is_service_message(message: Message) -> bool:
    if message.new_chat_members or message.left_chat_member:
        return True
    return False


def chat_type_is_private(message: Message):
    return message.chat.type == "private"


def chat_type_is_not_private(message: Message):
    return not chat_type_is_private(message)
