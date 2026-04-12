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
    if item.get("price_tag"):
        price_str = f"💰 {item['price_tag']}"
        if item.get("negotiable"):
            price_str += " (торг)"
        if item.get("arranged"):
            price_str += "\n🤝 Договорная"
    else:
        price_str = "💰 Цена не указана"

    return f"<b>{index}. {title}</b>\n{price_str} \n {url}"

def filter_message(data) -> str:
    message = "<b>Настройка фильтров: </b>\n\n"
    max_price = data.get("max_price", None)
    min_price = data.get("min_price", None)
    sorting = data.get("sorting", 0)
    if max_price is not None:
        message += f"Максимальная цена: <b>{max_price}</b>\n"
    else:
        message += f"Максимальная цена: <b>Не указана</b>\n"
    if min_price is not None:
        message += f"Минимальная цена: <b>{min_price}</b>\n"
    else:
        message += f"Минимальная цена: <b>Не указана</b>\n"
    if sorting == "ascending":
        message += f"Сортировка: <b>По возрастанию</b>\n"
    elif sorting == "descending":
        message += f"Сортировка: <b>По убыванию</b>\n"
    else:
        message += f"Сортировка: <b>Не указана</b>\n"
    return message