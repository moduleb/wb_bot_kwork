import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Router, filters, types
from dao import user_service
from db import AsyncSessionLocal
from keyboards import command_list_kb
from text import errors, messages
from utills.checkings import is_admin
from utills.send_photo_msg import send_photo_by_photo_id, SendPhotoError

if TYPE_CHECKING:
    from dao.models import User

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("list"))
async def get_all_items(msg: types.Message):

    bot: Bot = msg.bot
    user_tg_id = msg.from_user.id
    chat_id = msg.chat.id

    try:
        async with AsyncSessionLocal() as session:
            user: User = await user_service.get_or_create(session, user_tg_id=user_tg_id)

            # Проверка доступа
            if not is_admin(user_tg_id) and not user.is_active:
                await msg.answer(errors.access_denied)
                return

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
                await send_photo_by_photo_id(
                    bot=bot,
                    chat_id=chat_id,
                    photo_id=item.photo_tg_id,
                    photo_url=item.photo_url,
                    text=text,
                    reply_markup=command_list_kb.delete(item.id))

            except SendPhotoError as e:
                logger.warning("Ошибка при отправке изображения\n."
                               "Error: %s\n", str(e))
