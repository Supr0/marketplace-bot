import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.bot import setup_handlers
from sources.olx import OlxSource, close_session

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=getenv("LOG_LEVEL", "INFO"))
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    source = OlxSource()
    setup_handlers(dp, source=source)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_session()

if __name__ == "__main__":
    asyncio.run(main())