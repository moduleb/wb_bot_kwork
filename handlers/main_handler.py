import logging

from aiogram import Router, filters, types

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("start"))
async def start_handler(msg: types.Message):

    await msg.answer(text="Hello")
