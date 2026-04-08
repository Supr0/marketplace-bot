from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from parser.parser import PAGE_LIMIT

start_keyboard = [[
    types.InlineKeyboardButton(text="Искать товары", callback_data="lookup_goods")
]]



def listing_keyboard(items: list[dict], offset: int, query: str, has_next: bool) -> InlineKeyboardMarkup:
    rows = [[
    types.InlineKeyboardButton(text="Новый запрос", callback_data="change_lookup")
]]
    # for i, item in enumerate(items):
    #     rows.append([
    #         InlineKeyboardButton(
    #             text=f"🔗 {i + 1}. Відкрити",
    #             url=item["url"],
    #         )
    #     ])

    if has_next:
        rows.append([
            InlineKeyboardButton(
                text="⬇️ Завантажити ще",
                callback_data=f"more:{query}:{offset + PAGE_LIMIT}",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)