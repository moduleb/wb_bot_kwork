greeting_admin_msg = "Hello, Admin!"

greeting_user_msg = ("Hello!\n"
                   "Я бот, отслеживающий цены на Wildberries\n"
                   "Просто пришли мне ссылку на товар и я сообщю ,когда цена изменится.")


help_user_msg = ("/help    Справка\n"
    "/list    Список отслеживаний")

help_admib_msg = ("/help    Справка\n"
    "/list    Список отслеживаний\n"
    "/add    Добавить пользователя в бот, ожидает ник или id.\n"
    "/delete    Запретить пользователю пользоваться ботом.")


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
