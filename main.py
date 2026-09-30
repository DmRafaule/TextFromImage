import io
import sys
import logging
import asyncio

from PIL import Image
import pytesseract

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, BufferedInputFile, InlineQuery, InlineQueryResultPhoto
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

# Создание диспечера
bot_dispatcher = Dispatcher()
# Получение токена
with open(".env", "r") as file:
    buffer = file.read()
    line_pos = buffer.find("BOT_TOKEN")
    TOKEN = buffer[buffer.find("=", line_pos) + 1:buffer.find("\n", line_pos)]
# Настройка переводов
# Set up translation
i18n = I18n(path="locales", domain="messages")
i18n_handler = SimpleI18nMiddleware(i18n)
i18n_handler.setup(bot_dispatcher)

def split_text(text: str, max_length: int = 4000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@bot_dispatcher.message(F.photo)
async def image2text(message: Message):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    downloaded = await message.bot.download_file(file_info.file_path)

    image_bytes = downloaded.read()
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang="rus+eng")

    if text:
        for chunk in split_text(text):
            await message.answer(chunk, parse_mode=None)
    else:
        await message.answer(_("Увы не смог извлечь текст."))

@bot_dispatcher.message(Command('help'))
async def help(message: Message):
    await message.answer(_("Автор <b>TimTheWebmaster</b>"))
    await message.answer(_("""
Это экстрактор текста из изображений.
Просто отправь изображение в чат и бот вернёт весь текст обнаруженный на изображении.
Поддерживает кириллицу и латиницу
Поддерживаемые форматы изображений:
 * <b>PNG</b>
 * <b>JPEG</b>
 * <b>TIFF</b>
 * <b>GIF</b>
 * <b>WebP</b>
 * <b>BMP</b>
 * <b>PNM</b>
    """))
    await message.answer(_("Ещё больше ботов на @timthewebmaster"))

async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ))
    await bot_dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
