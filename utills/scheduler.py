import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove
from dao import item_service
from db import AsyncSessionLocal
from text import messages
from utills import parser_async
from utills.send_photo_msg import send_photo_by_photo_id, SendPhotoError

if TYPE_CHECKING:
    from dao.models import Item

logger = logging.getLogger(__name__)


async def notify_price_changes(bot: Bot):
    # Получаем все записи из бд
    async with AsyncSessionLocal() as session:
        items: list[Item] = await item_service.get_all(session)

        # Счетчик товаров, у которых изменилась цена
        modified_items_count = 0
        # Список id товаров где была ошибка
        items_parsing_errors_count = 0
        # Счетчик отправленных сообщений
        sent_messages_count = 0

        for item in items:
            try:
                # Получаем инфо о товаре и парсим прайс
                data = await parser_async._get_data(item.api_url)
                item_info_dict = parser_async._extract_product_info(data)
                new_price: float = item_info_dict.get("price")
                old_price: float = item.price
                if old_price == new_price:
                    continue

            except parser_async.ParserError as e:
                logger.warning("Ошибка при парсинге информации о товаре: item.id = %s\n"
                    "Error: %s", item.id, e)
                items_parsing_errors_count += 1

            # Если цена изменилась, отправляем сообщение и обновляем инфо в бд
            else:
                item.price = new_price
                await item_service.save(session, item)
                modified_items_count += 1

                full_item: Item = await item_service.get_item(session, item.origin_url)
                users = full_item.users

                for user in users:
                    try:
                        text = messages.price_changed.format(
                            old_price=old_price,
                            new_price=new_price,
                            title=item.title,
                            origin_url=item.origin_url)

                        await send_photo_by_photo_id(
                            bot=bot,
                            chat_id=user.tg_id,
                            photo_id=item.photo_tg_id,
                            photo_url=item.photo_url,
                            text=text,
                            reply_markup=ReplyKeyboardRemove())

                        sent_messages_count += 1

                    except SendPhotoError as e:
                        logger.warning("Ошибка при отправке изображения\n."
                                       "Error: %s\n", e)

    # Выводим статистику
    msg = (
        f"\nОбновлено товаров: {modified_items_count}\n"
        f"Отправлено уведомлений: {sent_messages_count}\n"
        f"Ошибок при парсинге товаров: {items_parsing_errors_count}\n"
    )

    logger.info(msg)



async def loop_check_price(bot: Bot, timeout: int):
    while True:
        try:
            await notify_price_changes(bot)

        except Exception:
            logging.exception("Ошибка во время выполнения Check price!")
        else:
            logging.info("Check price done successfully :-)")
        finally:
            logging.info("Sleep %s seconds...", timeout)
            await asyncio.sleep(timeout)
