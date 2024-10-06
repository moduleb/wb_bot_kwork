import logging

from asyncpg import exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from db import DBError
from models import Item

logger = logging.getLogger(__name__)


async def get_item(session: AsyncSession, item_data: dict) -> Item | None:
    """Ищем item в базе данных.

    Returns:
       Возвращает экземлпяр Item или None если ничего не найдено.

    """
    return await crud.get_one_by_filters(session, model=Item, **item_data)


def create(item_data: dict) -> Item:
    """Создает объект Item.

    Returns:
        Возвращает экземлпяр Item

    """
    return Item(**item_data)


async def save(session: AsyncSession, item: Item) -> None:
    """Сохраняем товар в бд.

    Raises:
        DBError:
            1. Вызывается при попытке сохранить экземляр item,
            когда не заполенны поля с ограничением'not null'.

            2. При попытки сохранения идентичного item.

        Ошибки подключения к базе данных обработаем на уровень выше.

    """
    try:
        await crud.save_one(session, obj=item)

    except exceptions.NotNullViolationError as e:
        msg = ("Ошибка при сохранении экземпляра Item\n"
                     "Не все поля заполнены\n")
        logger.exception(msg)
        raise DBError(msg) from e

    except IntegrityError as e:
        msg = ("Товар уже существует")
        logger.exception(msg)
        raise DBError(msg) from e
