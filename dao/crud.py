# crud.py
import logging
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from dao.models import Base

logger = logging.getLogger(__name__)

# Определяем тип переменной для модели
M = TypeVar("M", bound=Base)


# ----- CREATE ------------------------------------------------------------------------
async def save_one(session: AsyncSession, obj: type[M]) -> None:
    """Сохраняет объект в базу данных."""
    session.add(obj)
    await session.commit()


async def save_all(session: AsyncSession, objs: list[type[M]]) -> None:
    """Сохраняет объекты в базу данных."""
    session.add_all(objs)
    await session.commit()


# ----- READ --------------------------------------------------------------------------
async def get_all(session: AsyncSession, model: type[M]) -> list[M]:
    query = select(model)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_one_by_filters(session: AsyncSession,
                            model: type[M],
                            **filters) -> M | None:

    # Начинаем строить запрос
    query = select(model)

    # Применяем фильтры
    for key, value in filters.items():
        if hasattr(model, key):
            query = query.where(getattr(model, key) == value)
        else:
            logger.debug("Invalid filter key: %s."
                         "No such attribute in model: %s", key, value)

    # Выполняем запрос
    result = await session.execute(query)
    result_tuple = result.first()
    return result_tuple[0] if result_tuple else None


# ----- DELETE ------------------------------------------------------------------------
async def delete(session: AsyncSession, obj: object) -> None:
    """Удаляет объект из базы данных."""
    await session.delete(obj)
    await session.commit()
