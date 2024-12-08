import re

from aiogram.enums import MessageEntityType, ParseMode
from aiogram.types import Message
from aiogram.utils.markdown import markdown_decoration as md


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2.
    :param text: Текст для экранирования.
    :return: Экранированный текст.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def extract_markdown_v2_text(message: Message) -> str:
    """
    Восстанавливает текст сообщения с учетом форматирования в MarkdownV2.
    :param message: Объект Message из Telegram.
    :return: Текст с форматированием в MarkdownV2.
    """
    if not message.entities:
        return message.text

    entities = sorted(message.entities, key=lambda e: e.offset)  # Сортируем по позиции
    formatted_text = ""
    last_offset = 0

    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length

        formatted_text += escape_markdown_v2(message.text[last_offset:start])

        entity_text = message.text[start:end]
        if entity.type == MessageEntityType.BOLD:
            formatted_text += md.bold(entity_text)
        elif entity.type == MessageEntityType.ITALIC:
            formatted_text += md.italic(entity_text)
        elif entity.type == MessageEntityType.UNDERLINE:
            formatted_text += md.underline(entity_text)
        elif entity.type == MessageEntityType.STRIKETHROUGH:
            formatted_text += md.strikethrough(entity_text)
        elif entity.type == MessageEntityType.CODE:
            formatted_text += md.code(entity_text)
        elif entity.type == MessageEntityType.PRE:
            formatted_text += md.pre(entity_text)
        elif entity.type == MessageEntityType.SPOILER:
            formatted_text += md.spoiler(entity_text)
        elif entity.type == MessageEntityType.TEXT_LINK:
            formatted_text += md.link(entity_text, entity.url)
        elif entity.type == MessageEntityType.TEXT_MENTION:
            formatted_text += md.link(entity_text, f"tg://user?id={entity.user.id}")
        else:
            formatted_text += escape_markdown_v2(entity_text)

        last_offset = end

    formatted_text += escape_markdown_v2(message.text[last_offset:])
    return formatted_text


async def duplicate_message(message: Message, bot, target_chat_id: int):
    """
    Дублирует исходное сообщение в другой чат.
    Поддерживает текст, фото, видео, документы и аудио.
    :param message: Исходное сообщение.
    :param bot: Экземпляр бота.
    :param target_chat_id: ID чата, куда отправить дубликат.
    """
    if message.text or message.caption:
        text = message.text or message.caption
        entities = message.entities or message.caption_entities
        if entities:
            text = extract_markdown_v2_text(message)

    if message.text or message.caption:
        await bot.send_message(
            chat_id=target_chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    if message.photo:
        photo = message.photo[-1]
        await bot.send_photo(
            chat_id=target_chat_id,
            photo=photo.file_id,
            caption=text if message.caption else None,
            parse_mode=ParseMode.MARKDOWN_V2 if message.caption_entities else None
        )

    if message.video:
        await bot.send_video(
            chat_id=target_chat_id,
            video=message.video.file_id,
            caption=text if message.caption else None,
            parse_mode=ParseMode.MARKDOWN_V2 if message.caption_entities else None
        )

    if message.document:
        await bot.send_document(
            chat_id=target_chat_id,
            document=message.document.file_id,
            caption=text if message.caption else None,
            parse_mode=ParseMode.MARKDOWN_V2 if message.caption_entities else None
        )

    if message.audio:
        await bot.send_audio(
            chat_id=target_chat_id,
            audio=message.audio.file_id,
            caption=text if message.caption else None,
            parse_mode=ParseMode.MARKDOWN_V2 if message.caption_entities else None
        )

    if message.voice:
        await bot.send_voice(
            chat_id=target_chat_id,
            voice=message.voice.file_id,
            caption=text if message.caption else None,
            parse_mode=ParseMode.MARKDOWN_V2 if message.caption_entities else None
        )

    if message.video_note:
        await bot.send_video_note(
            chat_id=target_chat_id,
            video_note=message.video_note.file_id
        )