import logging

from aiogram import Router, filters, types
from text import messages

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("start"))
async def start_handler(msg: types.Message):
    await msg.answer(text="Hello")


@router.message(filters.Command("help"))
async def help_handler(msg: types.Message):
    await msg.answer(messages.help_msg)
