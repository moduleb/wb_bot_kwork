greeting_admin_msg = "Hello, Admin!"

greeting_user_msg = ("Hello!\n"
                   "Я бот, отслеживающий цены на Wildberries\n"
                   "Просто пришли мне ссылку на товар и я сообщю ,когда цена изменится.")


help_user_msg = ("/help\tСправка\n"
    "/list\tСписок отслеживаний")

help_admib_msg = ("/help\tСправка\n"
    "/list\tСписок отслеживаний"
    "/add\tДобавить пользователя в бот, ожидает ник или id.\n"
    "/delete\tЗапретить пользователю пользоваться ботом.")


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
