import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from dao import item_service
from db import AsyncSessionLocal
from text import messages
from utills import parser_async

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
        items_parsing_errors_ids = []

        # Счетчик отправленных сообщений
        sent_messages_count = 0
        # Счетчик ошибок при отравке сообщений
        sent_messages_err_count = 0

        for item in items:
            try:
                # Получаем инфо о товаре и парсим прайс
                data = await parser_async._get_data(item.api_url)
                item_info_dict = parser_async._extract_product_info(data)
                new_price: float = item_info_dict.get("price")
                old_price: float = item.price
                if ld_price == new_price:
                    logger.debug("Цена не изменилась у item_id: %s", item.id)
                    continue

            except parser_async.ParserError as e:
                logger.warning("Ошибка при парсинге информации о товаре: item.id = %s\n"
                    "Error: %s", item.id, e)
                items_parsing_errors_ids.append(item.id)

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

                        await bot.send_photo(chat_id=user.tg_id,
                                        photo=item.photo_tg_id,
                                        caption=text,
                                        parse_mode="Markdown")

                    except Exception:
                        logger.exception("Ошибка при отправке сообщения с фото по "
                                            "photo_tg_id: %s.", item.photo_tg_id)
                        sent_messages_err_count += 1
                    else:
                        logger.debug("Пользователю tg_id: %s отправлено сообщение об "
                                                        "изменении цены.", user.tg_id)
                        sent_messages_count += 1

        # Выводим статистику
        msg = (f"\nОбновлено товаров: {modified_items_count}\n"
            f"Отправлено уведомлений: {sent_messages_count}\n"
            f"Ошибок при парсинге товаров: {len(items_parsing_errors_ids)}\n"
            f"Ошибок при отравке уведомлений: {sent_messages_err_count}")
        if items_parsing_errors_ids:
            items_parsing_errors_ids_msg = (f"ID товаров в которых возникли ошибки "
                                            f"при парсинге: {items_parsing_errors_ids}")
            msg = msg + "\n" + items_parsing_errors_ids_msg
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
