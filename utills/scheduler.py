import asyncio
import logging

from aiogram import Bot
from dao import item_service
from db import AsyncSessionLocal
from text import messages
from utills import parser_async

logger = logging.getLogger(__name__)


async def notify_price_changes(bot: Bot):
    # Получаем все записи из бд
    async with AsyncSessionLocal() as session:
        items = await item_service.get_all(session)

        for item in items:
            # Получаем инфо о товаре и парсим прайс
            data = await parser_async._get_data(item.api_url)
            item_info_dict = parser_async._extract_product_info(data)
            new_price = item_info_dict["price"]
            old_price = item.price

            # Если цена изменилась, отправляем сообщение и обновляем инфо в бд
            if new_price != old_price:
                item.price = new_price
                await item_service.save(session, item)

                origin_url = item.origin_url
                full_item = await item_service.get_item(session, origin_url)
                users = full_item.users

                for user in users:
                    text = messages.price_changed.format(
                        old_price=old_price,
                        new_price=new_price,
                        title=item.title,
                        origin_url=item.origin_url
                    )
                    origin_url=item.origin_url
                    print(text)
                    print(origin_url)
                    try:
                        await bot.send_photo(chat_id=user.tg_id,
                                        photo=item.photo_tg_id,
                                        caption=text,
                                        parse_mode="Markdown")

                        logger.debug("Пользователю tg_id: %s отправлено сообщение об изменении цены",
                                     user.tg_id)

                    except Exception:
                        logger.exception("Ошибка при сообщения с фото по photo_tg_id: %s",
                                         item.photo_tg_id)


async def loop_check_price(bot: Bot, timeout: int):
    try:
        while True:
            await notify_price_changes(bot)
            logging.debug("Check price...")
            await asyncio.sleep(timeout)

    except Exception as e:
        logging.exception(str(e))
