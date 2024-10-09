import asyncio
import logging

from aiogram import F, Router, types

from dao import item_service, user_service
from db import AsyncSessionLocal
from text import errors
from utills.checkings import is_admin

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("del"))
async def delete(callback: types.CallbackQuery):

    user_tg_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id=user_tg_id)

            # Проверка доступа
            if not is_admin(user_tg_id) and not user.is_active:
                await msg.answer(errors.access_denied)
                return

            for i, item in enumerate(user.items):
                if item.id == item_id:
                    user.items.pop(i)
                    await user_service.save_user(user=user, session=session)

                    item = await item_service.get_item(session, origin_url=item.origin_url)
                    item_users = item.users
                    if not item_users:
                        await item_service.delete(session, item)
                    await callback.message.delete()
                    break

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await callback.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await callback.answer(text=errors.service_unavailable_error)
