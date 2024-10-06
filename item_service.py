import logging

from asyncpg import exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from db import DBDublicateError, DBError
from models import Item

logger = logging.getLogger(__name__)


async def get(item_data: dict, session: AsyncSession) -> Item | None:

    logger.debug("Поиск уже существующего item в базе данных:\n"
                "Title: %s", item_data.get("title"))

    items = await crud.get_many_by_filters(session=session,
                                           model=Item,
                                           load_relationships=True,
                                           **item_data)

    logger.debug("Найдены объекты: %s", items)

    return items[0] if items else None


def create(item_data: dict):
    return Item(**item_data)


async def save(item: Item, session: AsyncSession) -> None:
    """Сохраняем товар в бд."""
    try:
        await crud.save_one(session=session,
                            obj=item)

    except exceptions.NotNullViolationError as e:
        logger.exception("Ошибка при сохранении экземпляра Item\n"
                     "Не все поля заполнены\n")
        raise DBError.not_null_constrain() from e

    except IntegrityError:
        logger.debug("Товар уже существует")
        raise DBDublicateError


async def delete_all(session: AsyncSession, items: list) -> None:

    logger.debug("Удаляем items: %s", items)
    await crud.delete_many(session=session, objs=items)
