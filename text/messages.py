from text.commands import commands

help_msg = "\n".join(f"/{command}\t{description}" for command, description in commands.items())

item_info = (
    "[{title}]({origin_url})\n"
    "Цена: {price} руб."
)

price_changed = (
    "Изменилась цена на товар:\n"
    "[{title}]({origin_url})\n"
    "Старая цена: {old_price} руб.\n"
    "Новая цена: {new_price} руб."
)
