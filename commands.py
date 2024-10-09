import logging

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from settings import settings

logger = logging.getLogger(__name__)


user_commands = [
    types.BotCommand(command="start", description="Запустить бота"),
    types.BotCommand(command="list", description="Список отслеживаний"),
    types.BotCommand(command="help", description="Справка"),
]

admin_commands = [*user_commands,
    types.BotCommand(command="add", description="Добавить пользователя"),
    types.BotCommand(command="delete", description="Удалить пользователя"),
]


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(commands=user_commands,
                              scope=types.BotCommandScopeAllPrivateChats())

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=types.BotCommandScopeChat(chat_id=admin_id))

        except TelegramBadRequest:
            logger.warning("Can't set commands to admin with ID %s", admin_id)
