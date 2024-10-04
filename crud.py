# db/crud.py
import logging
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Base

logger = logging.getLogger(__name__)


# ----- CREATE ------------------------------------------------------------------------
async def save_one(session: AsyncSession, obj: object) -> None:
    """Сохраняет объект в базу данных."""
    session.add(obj)
    await session.commit()


async def save_many(session: AsyncSession, objs: list[object]) -> None:
    """Сохраняет объекты в базу данных."""
    session.add_all(objs)
    await session.commit()


# ----- READ --------------------------------------------------------------------------
# Определяем тип переменной для модели
M = TypeVar("M", bound=Base)


async def get_many_by_filters(
        session: AsyncSession,
        model: M,
        **filters) -> list[M]:

    # Начинаем строить запрос
    query = select(model)

    # Применяем фильтры
    for key, value in filters.items():
        if hasattr(model, key):
            query = query.where(getattr(model, key) == value)
            logger.debug("Query: \n%s", query)
        else:
            logger.debug(f"Invalid filter key: {key}. No such attribute in model: {model}")

    # Выполняем запрос
    result = await session.execute(query)
    return list(result.scalars().all())


# ----- DELETE ------------------------------------------------------------------------
async def delete_one(session: AsyncSession, obj: object) -> None:
    """Удаляет объект из базы данных."""
    await session.delete(obj)
    await session.commit()


async def delete_many(session: AsyncSession, objs: list[object]) -> None:
    """Удаляет объекты из базы данных"""
    # Удаляем каждый объект из сессии по одному
    for obj in objs:
        await session.delete(obj)
    await session.commit()
