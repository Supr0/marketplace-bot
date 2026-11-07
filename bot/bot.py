import logging

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from core import errors
from core.models import SearchQuery
from core.ports import MarketplaceSource
from .keyboards import start_keyboard, listing_keyboard, filter_keyboard
from .messages import start_message, generate_item_card, filter_message
from .states import States, FilterStates


def setup_handlers(dp: Dispatcher, source: MarketplaceSource):
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
        data = await state.get_data()
        await state.update_data(query=query)
        await run_search(source, query, cursor=None, message_or_callback=message, data=data)

    @dp.callback_query(F.data.startswith("more:"))
    async def on_load_more(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        query = data.get("query", "")
        if not query:
            await callback.answer("Сессия истекла.")
            return
        _, cursor, visual_offset = callback.data.split(":", 2)
        visual_offset = int(visual_offset)
        await callback.answer()
        await run_search(source, query, cursor=cursor, message_or_callback=callback, data=data, visual_offset=visual_offset)

    @dp.callback_query(F.data == "filters", StateFilter(None))
    @dp.callback_query(F.data == "filters", States.lookup_state)
    async def on_filters(callback: CallbackQuery, state: FSMContext):
        markup = InlineKeyboardMarkup(inline_keyboard=filter_keyboard)
        message = filter_message(await state.get_data())
        await state.set_state(FilterStates.filter_state)
        await callback.message.answer(message, reply_markup=markup, parse_mode="html")
        await callback.answer()

    @dp.callback_query(F.data == "max_price", FilterStates.filter_state)
    @dp.callback_query(F.data == "min_price", FilterStates.filter_state)
    @dp.callback_query(F.data == "max_price", FilterStates.min_price_state)
    @dp.callback_query(F.data == "min_price", FilterStates.max_price_state)
    async def on_price_bracket(callback: CallbackQuery, state: FSMContext):
        min_or_max , _ = callback.data.split('_',1)
        if min_or_max == "min":
            await state.set_state(FilterStates.min_price_state)
            await callback.answer("Укажите минимальную цену")
        else:
            await state.set_state(FilterStates.max_price_state)
            await callback.answer("Укажите максимальную цену")

    @dp.callback_query(F.data == "ascending_price", FilterStates.filter_state)
    @dp.callback_query(F.data == "descending_price", FilterStates.filter_state)
    async def on_price_sort(callback: CallbackQuery, state: FSMContext):
        ascending_or_descending , _ = callback.data.split('_',1)
        await state.update_data(
            sorting=ascending_or_descending
        )
        markup = InlineKeyboardMarkup(inline_keyboard=filter_keyboard)
        message = filter_message(await state.get_data())
        await callback.answer("Обновлено")
        await callback.message.edit_text(message, reply_markup=markup, parse_mode="html")

    @dp.message(FilterStates.min_price_state)
    async def on_min_price(message: Message, state: FSMContext):
        try:
            max_price = (await state.get_data()).get("max_price")
            min_price = int(message.text)
            if max_price is None or max_price >= min_price:
                markup = InlineKeyboardMarkup(inline_keyboard=filter_keyboard)
                await state.update_data(
                    min_price=min_price
                )
                await state.set_state(FilterStates.filter_state)
                await message.answer(filter_message(await state.get_data()), reply_markup=markup, parse_mode="html")
            else:
                await message.answer("Минимальная цена не может быть больше максимальной")
        except ValueError:
            await message.answer("Введите число")

    @dp.message(FilterStates.max_price_state)
    async def on_max_price(message: Message, state: FSMContext):
        try:
            min_price = (await state.get_data()).get("min_price")
            max_price = int(message.text)
            if min_price is None or max_price >= min_price:
                markup = InlineKeyboardMarkup(inline_keyboard=filter_keyboard)
                await state.update_data(
                    max_price=max_price
                )
                await state.set_state(FilterStates.filter_state)
                await message.answer(filter_message(await state.get_data()), reply_markup=markup, parse_mode="html")
            else:
                await message.answer("Максимальная цена не может быть мень минимальной")
        except ValueError:
            await message.answer("Введите число")

    @dp.callback_query(F.data == "reset_filters", FilterStates.filter_state)
    async def on_reset_filters(callback: CallbackQuery, state: FSMContext):
        await state.update_data(
            max_price=None,
            min_price=None,
            sorting=None
        )
        markup = InlineKeyboardMarkup(inline_keyboard=filter_keyboard)
        await callback.message.edit_text(filter_message(await state.get_data()), reply_markup=markup, parse_mode="html")
        await callback.answer("Фильтры сброшены")

    @dp.callback_query(F.data == "apply_filters", FilterStates.filter_state)
    async def on_apply_filters(callback: CallbackQuery, state: FSMContext):
        markup = InlineKeyboardMarkup(inline_keyboard=start_keyboard)
        await state.set_state(None)
        await callback.message.answer("Что вы хотите сделать?", reply_markup=markup)
        await callback.answer("Фильтры применены")

    @dp.callback_query
    async def on_unhandled_callback(callback: CallbackQuery):
        await callback.answer()



async def run_search(source: MarketplaceSource, query: str, cursor: str | None, message_or_callback, data = None,
                     visual_offset: int = 0):
    """Shared logic for first search and load-more."""
    is_callback = isinstance(message_or_callback, CallbackQuery)
    send = message_or_callback.message if is_callback else message_or_callback
    status_msg = await send.answer("🔍 Ищю обьявления…")

    try:
        page = await source.search(
            SearchQuery(
                query=query,
                price_from=(data or {}).get("min_price"),
                price_to=(data or {}).get("max_price"),
                sorting=(data or {}).get("sorting"),
                cursor=cursor
            )
        )
    except errors.SourceUnavailable as e:
        await status_msg.delete()
        await send.answer(f"❌ Маркетплейс недоступен, попробуйте позже")
        return
    except errors.SourceRejectedQuery:
        await status_msg.delete()
        await send.answer("❌ Маркетплейс отклонил запрос, попробуйте позже")
        return
    except errors.MarketplaceError as e:
        await status_msg.delete()
        await send.answer(f"❌ Что-то пошло не так: {e}")
        return
    except Exception as e:
        logging.exception("Lookup exception:")
        await status_msg.delete()
        await send.answer(f"❌ Что-то пошло не так: {e}")
        return

    await status_msg.delete()

    if not page.items:
        await send.answer(
            "😕 <b>Ничего не найдено.</b>\n\nПопробуйте другой запрос.",
            parse_mode="HTML",
        )
        return

    start = visual_offset
    shown_so_far = start + len(page.items)
    keyboard = listing_keyboard(page.next_cursor, shown_so_far)
    cards = "\n\n".join(generate_item_card(item, start + i + 1) for i, item in enumerate(page.items))
    header = f"📦 Найдено <b>{page.total}</b> обьявлений. Отображаю {shown_so_far}:\n"
    text = header + "\n" + cards

    if len(text) > 4000:
        text = text[:4000] + "\n\n<i>…(сокращено)</i>"

    await send.answer(text, parse_mode="HTML", reply_markup=keyboard)

