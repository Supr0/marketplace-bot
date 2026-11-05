import asyncio
import logging
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from bot.bot import setup_handlers
from parser.parser import close_session

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=getenv("LOG_LEVEL", "INFO"))
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    setup_handlers(dp)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_session()

if __name__ == "__main__":
    asyncio.run(main())