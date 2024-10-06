import asyncio
import logging

from aiogram import Bot, F, Router, filters, types

import item_service
import kb
import user_service
from db import AsyncSessionLocal, DBError
from parser_async import ParserError, UrlError, get_item_info
from text import errors, messages

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("start"))
async def start_handler(msg: types.Message):

    await msg.answer(text="Hello")


@router.message(filters.Command("list"))
async def get_all_items(msg: types.Message):

    bot: Bot = msg.bot
    user_tg_id = msg.from_user.id
    chat_id = msg.chat.id

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id=user_tg_id)

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await msg.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await msg.answer(text=errors.service_unavailable_error)

    else:
        items = user.items

        if not items:
            logger.debug("No Items у этого user")
            await msg.answer(text=errors.no_items_error)
            return

        for item in items:
            text = messages.item_info.format(title=item.title,
                                    origin_url=item.origin_url,
                                    price=item.price)

            await bot.send_photo(chat_id=chat_id,
                                photo=item.photo_tg_id,
                                caption=text,
                                parse_mode="Markdown",
                                reply_markup=kb.delete(item.id))


@router.callback_query(F.data.startswith("del"))
async def delete(callback: types.CallbackQuery):

    user_tg_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session, user_tg_id=user_tg_id)

    except (OSError, asyncio.exceptions.TimeoutError):
        logger.exception("База данных недоступна")
        await callback.answer(text=errors.service_unavailable_error)

    except Exception:
        logger.exception("Unexpected error")
        await callback.answer(text=errors.service_unavailable_error)

    else:
        for i, item in enumerate(user.items):
            if item.id == item_id:
                user.items.pop(i)
                await user_service.save_user(user=user, session=session)
                await callback.message.delete()
                break


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
            user = await user_service.get_or_create(session, user_tg_id=user_tg_id)

            item_data_dict = await get_item_info(origin_url)
            logger.debug("Получена информацию от парсера: %s", item_data_dict)

            # Извлекаем photo_url тк в модели Item нет такого поля.
            photo_url = item_data_dict.pop("photo_url")

            item = await item_service.get_item(session, item_data_dict)

            if item:
                if user in item.users:
                    await msg.answer(text=errors.item_dublicate_error)
                    logger.debug("Товар уже есть в списке у пользователя, return")
                    return
            else:
                item = item_service.create(item_data_dict)
                logger.debug("Создаен новый объект Item: %s", item)

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
