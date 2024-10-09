import asyncio
import logging

from aiogram import Bot, Router, types
from aiohttp.client_exceptions import ClientResponseError
from dao import item_service, user_service
from db import AsyncSessionLocal, DBError
from text import errors, messages
from utills.checkings import is_admin
from utills.parser_async import ParserError, UrlError, get_item_info
from utills.send_photo_msg import send_photo_by_photo_url, SendPhotoError, send_photo_by_photo_id

router = Router()

logger = logging.getLogger(__name__)


# ANY MESSAGE
@router.message()
async def parse_url_handler(msg: types.Message):

    user_tg_id = msg.from_user.id
    origin_url: str = msg.text
    bot: Bot = msg.bot
    chat_id = msg.chat.id

    try:
        async with AsyncSessionLocal() as session:
            # async with engine.begin() as session:
            user = await user_service.get_or_create(session, user_tg_id)
            user_id = user.id
            logger.debug("Получен экземпляр User, id: %s", user_id)

            # Проверка доступа
            if not is_admin(user_tg_id) and not user.is_active:
                await msg.answer(errors.access_denied)
                return

            item_data_dict: dict = await get_item_info(origin_url)
            logger.debug("Получена информация от парсера: %s", item_data_dict)

            item = await item_service.get_item(session, origin_url)

            if item:
                item_id = item.id
                users_count = len(item.users)
                logger.debug("Получен экземпляр Item, id: %s\n"
                                "\tlen(item.users): %d", item_id, users_count)

                if user in item.users:
                    await msg.answer(text=errors.item_dublicate_error)
                    logger.debug("Товар уже есть в списке у пользователя, return")
                    return
            else:
                item = item_service.create(item_data_dict)
                logger.debug("Создаен новый объект Item")

            item.users.append(user)
            logger.debug("Прикрепляем user к item")

            text = messages.item_info.format(title=item.title,
                                            origin_url=item.origin_url,
                                            price=item.price)

            # Могут быть сохранены объекты без photo_url
            if not item.photo_url:
                item.photo_url = item_data_dict["photo_url"]

            try:
                if item.photo_tg_id:
                    photo_tg_id: str = await send_photo_by_photo_id(
                        bot=bot,
                        chat_id=chat_id,
                        text=text,
                        photo_url=item.photo_url,
                        photo_id=item.photo_tg_id,
                        reply_markup=types.ReplyKeyboardRemove())
                else:
                    photo_tg_id: str = await send_photo_by_photo_url(
                        bot=bot,
                        chat_id=chat_id,
                        text=text,
                        photo_url=item.photo_url,
                        reply_markup=types.ReplyKeyboardRemove())

                item.photo_tg_id = photo_tg_id

                await item_service.save(session, item)

            except SendPhotoError as e:
                logger.warning("Невозможно отправить изображение\n"
                    "Error: %s", str(e))
                await msg.answer(errors.item_add_err)

            else:
                await msg.answer(messages.item_added)

    except UrlError as e:
        await msg.answer(text=str(e))

    except ParserError:
        await msg.answer(text=errors.get_item_info_error)

    except DBError:
        await msg.answer(text=errors.service_unavailable_error)

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)
