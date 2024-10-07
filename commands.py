from aiogram import types
from text.commands import commands

user_commands = []
for command, description in commands.items():
    user_commands.append(
        types.BotCommand(command=command, description=description),
    )
