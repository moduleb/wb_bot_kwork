from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

cancel_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Cancel")]],
                                resize_keyboard=True)
