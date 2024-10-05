import logging

from asyncpg import exceptions

import crud
from sqlalchemy.ext.asyncio import AsyncSession
from models import User

logger = logging.getLogger(__name__)


async def get_or_create(tg_id: int, session: AsyncSession) -> User:
    """Поиск пользователя. Если не найден, создаем и сохраняем в бд."""
    # Ищем пользователя в базе
    user = await _get_user_by_tg_id(tg_id, session)
    logger.debug("Получен объект user: %s", user)

    # Создаем пользователя если не существует и сохраняем в бд.
    if not user:
        user = _create_user(tg_id=tg_id)
        logger.debug("Создaн объект User: %s", user)

        await _save_user(user, session)
        logger.debug("Объект User успешно сохранен")

    assert user is not None, "User должен быть найден в базе данных или создан"

    return user


async def _get_user_by_tg_id(tg_id: int, session: AsyncSession) -> User | None:
    """Поиск пользователя по id."""
    objs_list = await crud.get_many_by_filters(session=session,
                                                model=User,
                                                tg_id=tg_id)

    return objs_list[0] if objs_list else None


def _create_user(tg_id: int) -> User:
    """Создаем объект User."""
    return User(tg_id=tg_id)


async def _save_user(user: User, session: AsyncSession) -> None:
    """Сохраняем пользователя в бд."""
    try:
        await crud.save_one(
            session=session,
            obj=user)

    except exceptions.UniqueViolationError:
        logger.exception("Пользователь с таким tg_id уже существует")
        # Для пользователя эту ошибку игнорируем, ничего не сообщаем
