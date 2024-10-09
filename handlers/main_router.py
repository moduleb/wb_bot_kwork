import logging

from aiogram import F, Router, filters, types
from aiogram.fsm.context import FSMContext
from dao import user_service
from db import AsyncSessionLocal, DBError
from text import errors, messages
from utills.checkings import is_admin

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("start"))
async def start_handler(msg: types.Message):
    user_tg_id = msg.from_user.id

    if is_admin(user_tg_id):
        await msg.answer(messages.greeting_admin_msg)
        return

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id)
            user_id = user.id
            logger.debug("Получен экземпляр User, id: %s", user_id)

        if user.is_active:
            await msg.answer(messages.greeting_user_msg)
            return

        await msg.answer(errors.access_denied)

    except DBError:
        await msg.answer(text=errors.service_unavailable_error)

    except (OSError, TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)


@router.message(filters.Command("help"))
async def help_handler(msg: types.Message):

    user_tg_id = msg.from_user.id

    if is_admin(user_tg_id):
        await msg.answer(messages.help_admib_msg)
        return

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id)
            user_id = user.id
            logger.debug("Получен экземпляр User, id: %s", user_id)

        if user.is_active:
            await msg.answer(messages.help_user_msg)
            return

        await msg.answer(errors.access_denied)

    except DBError:
        await msg.answer(text=errors.service_unavailable_error)

    except (OSError, TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)


@router.message(F.text == "Cancel")
async def reset_state(message: types.Message, state: FSMContext):
    await state.clear()  # Сброс состояния
    await message.answer("Ok", reply_markup=types.ReplyKeyboardRemove())
