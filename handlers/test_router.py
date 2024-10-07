import asyncio
import logging

from aiogram import Router, filters, types
from dao import item_service, user_service
from db import AsyncSessionLocal
from text import errors

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("test"))
async def start_handler(msg: types.Message):

    await msg.answer("Через несколько секунд вам поступит сообщение(я) об изменении цены ваших товаров.")
    await asyncio.sleep(3)

    user_tg_id = msg.from_user.id

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id)

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)

    else:
        items = user.items
        for item in items:
            item.price = 1
        await item_service.save_all(session, items)
