import logging

from asyncpg import exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from dao import crud
from dao.models import User

logger = logging.getLogger(__name__)


async def get_or_create(session: AsyncSession, user_tg_id: int) -> User:
    """Поиск пользователя в базе данных.
        Если не найден, создаем и сохраняем в бд.

    Returns:
        Возвращает экземпляр User

    """
    # Ищем пользователя в базе
    user = await _get_user_by_tg_id(session, user_tg_id)

    # Создаем пользователя если не существует и сохраняем в бд.
    if not user:
        user = _create_user(user_tg_id)
        user_id = user.id
        logger.debug("Создaн объект User, id: %s", user_id)

        await save_user(session, user)
        user_id = user.id
        logger.debug("Объект User успешно сохранен, id: %s", user_id)

    return user


async def _get_user_by_tg_id(session: AsyncSession, user_tg_id: int) -> User | None:
    """Поиск пользователя по id.

    Returns:
        Возвращает экземляр User если найден, иначе None.

    """
    return await crud.get_one_by_filters(session, model=User, tg_id=user_tg_id)


def _create_user(user_tg_id: int) -> User:
    """Создаем объект User.

    Returns:
        Возвращает созданный экземляр User.

    """
    return User(tg_id=user_tg_id)


async def save_user(session: AsyncSession, user: User) -> None:
    """Сохраняем пользователя в базу данных."""
    try:
        await crud.save_one(session, user)
        logger.debug("User сохранен в бд")

    except exceptions.UniqueViolationError:
        logger.exception("Пользователь с таким tg_id уже существует")
        # Для пользователя эту ошибку игнорируем, ничего не сообщаем
