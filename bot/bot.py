import asyncio
import logging

import requests
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from .keyboards import start_keyboard, listing_keyboard
from .messages import start_message, generate_item_card
from parser.parser import parse_olx_response, parse_olx_endpoint
from .states import States


def setup_handlers(dp: Dispatcher):
    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        content = start_message
        markup = InlineKeyboardMarkup(inline_keyboard=start_keyboard)
        await message.answer(**content.as_kwargs(), reply_markup=markup)

    @dp.callback_query(F.data == "lookup_goods")
    @dp.callback_query(F.data == "change_lookup")
    async def on_lookup(message: Message, state: FSMContext) -> None:
        await message.answer("Введите поисковой запрос")
        await state.set_state(States.lookup_state)

    @dp.message(States.lookup_state)
    async def on_request(message: Message, state: FSMContext) -> None:
        query = message.text.strip()
        if not query:
            await message.answer("Введите поисковой запрос.")
            return
        await run_search(query, offset=0, message_or_callback=message)

    @dp.callback_query(F.data.startswith("more:"))
    async def on_load_more(callback: CallbackQuery):
        _, query, raw_offset = callback.data.split(":", 2)
        offset = int(raw_offset)
        await callback.answer()
        await run_search(query, offset=offset, message_or_callback=callback)


async def run_search(query: str, offset: int, message_or_callback):
    """Shared logic for first search and load-more."""
    is_callback = isinstance(message_or_callback, CallbackQuery)
    send = message_or_callback.message if is_callback else message_or_callback

    status_msg = await send.answer("🔍 Шукаю оголошення…")

    try:
        raw = await asyncio.get_event_loop().run_in_executor(
            None, parse_olx_endpoint, query, offset
        )
        items, has_next, total = parse_olx_response(raw)
    except requests.HTTPError as e:
        await status_msg.delete()
        await send.answer(f"❌ Помилка мережі: {e}")
        return
    except RuntimeError as e:
        await status_msg.delete()
        await send.answer(f"❌ OLX повернув помилку: {e}")
        return
    except Exception as e:
        logging.exception("Lookup exception:")
        await status_msg.delete()
        await send.answer(f"❌ Щось пішло не так: {e}")
        return

    await status_msg.delete()

    if not items:
        await send.answer(
            "😕 <b>Нічого не знайдено.</b>\n\nСпробуйте інший запит.",
            parse_mode="HTML",
        )
        return

    shown_so_far = offset + len(items)
    header = f"📦 Знайдено <b>{total}</b> оголошень. Показую {shown_so_far}:\n"

    cards = "\n\n".join(generate_item_card(item, offset + i + 1) for i, item in enumerate(items))
    text = header + "\n" + cards

    # Telegram message limit is 4096 chars — truncate gracefully
    if len(text) > 4000:
        text = text[:4000] + "\n\n<i>…(скорочено)</i>"

    keyboard = listing_keyboard(items, offset, query, has_next)
    await send.answer(text, parse_mode="HTML", reply_markup=keyboard)

