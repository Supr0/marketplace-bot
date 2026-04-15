from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_keyboard = [[
    types.InlineKeyboardButton(text="🔍 Искать товары", callback_data="lookup_goods"),
    types.InlineKeyboardButton(text="⚙️ Настроить фильтры", callback_data="filters")
]]

filter_keyboard = [[
    types.InlineKeyboardButton(text="🔺 Максимальная цена", callback_data="max_price"),
    types.InlineKeyboardButton(text="🔻 Минимальная цена", callback_data="min_price")
],[
    types.InlineKeyboardButton(text="⤴️ По возрастанию", callback_data="ascending_price"),
    types.InlineKeyboardButton(text="⤵️ По убыванию", callback_data="descending_price")
],[
    types.InlineKeyboardButton(text="🟢 Применить", callback_data="apply_filters"),
    types.InlineKeyboardButton(text="🔴 Сбростить фильтры", callback_data="reset_filters")
]
]

def listing_keyboard(items: list[dict], offset: int, query: str, has_next: bool, visual_offset:int) -> InlineKeyboardMarkup:
    rows = [[
    types.InlineKeyboardButton(text="🔍 Новый запрос", callback_data="change_lookup"),
    types.InlineKeyboardButton(text="⚙️ Настроить фильтры", callback_data="filters"),
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
                text="⬇️ Загрузить ещё",
                callback_data=f"more:{query}:{offset}:{visual_offset}",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)