from aiogram.utils.formatting import as_list, Bold, as_numbered_section

start_message = as_list(
    Bold("Привет! Я бот который помогает искать товары на OLX! \n\n"),
    as_numbered_section(
        Bold("Как мной пользоватся: "),
            "Нажми на кнопку " + "\"Искать товары\" ",
            "Напиши название товара который ищешь.",
            "Отправь мне и я покажу список товаров подходящих под твой запрос.",
            "Нажми " + "\"Обнвить\" " + " чтобы обновить товары или " + "\"Новый запрос\" " +
            " чтобы написать новый запрос!"
    )
)

def generate_item_card(item: dict, index: int) -> str:
    title = item["title"]
    url = item["url"]
    if item.get("arranged"):
        price_str = "🤝 Договірна"
    elif item.get("price_tag"):
        price_str = f"💰 {item['price_tag']}"
        if item.get("negotiable"):
            price_str += " (торг)"
    else:
        price_str = "💰 Ціна не вказана"

    return f"<b>{index}. {title}</b>\n{price_str} \n {url}"
