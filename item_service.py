import logging

from asyncpg import exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from db import DBDublicateError, DBError
from models import Item

logger = logging.getLogger(__name__)


async def get(item_data: dict, session: AsyncSession) -> Item | None:
    if item := await crud.get_many_by_filters(session=session,
                                              model=Item,
                                              **item_data):
        return item[0]


def create(data: dict) -> Item:
    """Создает объект Item."""
    return Item(**data)


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
