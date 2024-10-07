import asyncio
import logging

from aiogram import Bot, Router, filters, types

from keyboards import command_list_kb
from dao import user_service
from db import AsyncSessionLocal
from text import errors, messages

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("list"))
async def get_all_items(msg: types.Message):

    bot: Bot = msg.bot
    user_tg_id = msg.from_user.id
    chat_id = msg.chat.id

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id=user_tg_id)

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)

    else:
        items = user.items

        if not items:
            logger.debug("No Items у этого user")
            await msg.answer(text=errors.no_items_error)
            return

        for item in items:
            text = messages.item_info.format(title=item.title,
                                    origin_url=item.origin_url,
                                    price=item.price)
            try:

                await bot.send_photo(chat_id=chat_id,
                                    photo=item.photo_tg_id,
                                    caption=text,
                                    parse_mode="Markdown",
                                    reply_markup=command_list_kb.delete(item.id))
            except Exception:
                logger.exception("Ошибка при отправлении фото по photo_tg_id: %s",
                                 item.photo_tg_id)
