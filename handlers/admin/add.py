import logging
from typing import TYPE_CHECKING

from aiogram import Router, filters, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from dao import user_service
from db import AsyncSessionLocal, DBError
from keyboards.cancel import cancel_kb
from text import admin, errors
from utills.checkings import is_admin

if TYPE_CHECKING:
    from dao.models import User

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("add"))
async def start_handler(msg: types.Message, state: FSMContext):
    user_tg_id = msg.from_user.id

    if not is_admin(user_tg_id):
        await msg.answer(errors.access_denied_to_command)
        return

    await msg.answer(admin.wait_for_user_identity_to_add, reply_markup=cancel_kb)
    await state.set_state("wait_for_user_id_or_name")


@router.message(StateFilter("wait_for_user_id_or_name"))
async def set_user_status(msg: types.Message, state: FSMContext):
    user_tg_id = msg.from_user.id

    if not is_admin(user_tg_id):
        await msg.answer(errors.access_denied_to_command)
        return

    try:
        async with AsyncSessionLocal() as session:
            user: User = await user_service.get_or_create(session, user_tg_id)
            user_id = user.id
            logger.debug("Получен экземпляр User, id: %s", user_id)

        user_id_to_add = msg.text
        user_to_activate = None
        try:
            user_id_to_add = int(user_id_to_add)
            user_to_activate = await user_service.get_by_filter(session, tg_id=user_id_to_add)

        except ValueError:
            logger.debug("Полученное значение не является ID")

        # if not user_to_activate:
        #     user_to_activate = await user_service.get_by_filter(session, username=msg.from_user.username)

        if user_to_activate:
            logger.debug("Найден пользователь, id: %s", user_to_activate.id)

            if user_to_activate.is_active:
                await msg.answer(admin.user_already_added_err)
                await state.clear()
                return

            user_to_activate.is_active = True
            await user_service.save_user(session, user_to_activate)
            await msg.answer(admin.user_add_success)
            await state.clear()

        else:
            await msg.answer(admin.user_add_err)

    except DBError:
        await msg.answer(text=errors.service_unavailable_error)

    except (OSError, TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)
