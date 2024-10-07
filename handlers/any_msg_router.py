import asyncio
import logging

from aiogram import Bot, Router, types
from dao import item_service, user_service
from db import AsyncSessionLocal, DBError
from text import errors, messages
from utills.parser_async import ParserError, UrlError, get_item_info

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

            item_data_dict: dict = await get_item_info(origin_url)
            logger.debug("Получена информация от парсера: %s", item_data_dict)

            # Извлекаем photo_url тк в модели Item нет такого поля.
            photo_url = item_data_dict.pop("photo_url")

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

            input_file = types.input_file.URLInputFile(photo_url)

            text = messages.item_info.format(title=item.title,
                                            origin_url=item.origin_url,
                                            price=item.price)

            sent_msg: types.Message = await bot.send_photo(chat_id=chat_id,
                                            photo=input_file,
                                            caption=text,
                                            parse_mode="Markdown")

            photo_tg_id = sent_msg.photo[-1].file_id

            item.photo_tg_id = photo_tg_id

            await item_service.save(session, item)

            await msg.answer(text="Товар добавлен")

    #     disable_web_page_preview=True)

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
