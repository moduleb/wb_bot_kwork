import logging

from aiogram import Router, filters, fsm, types

import item_service
import photo_downloader
import user_service
from db import AsyncSessionLocal, DBDublicateError, DBError
from parser_async import ParserError, UrlError, get_item_info
from text import errors, messages
from photo_downloader import PhotoDownloaderError

router = Router()

logger = logging.getLogger(__name__)


@router.message(filters.Command("start"))
async def start_handler(msg: types.Message):

    await msg.answer(text="Hello")


@router.message()
async def parse_url_handler(msg: types.Message,
                        state: fsm.context.FSMContext):

    tg_id = msg.from_user.id
    url = msg.text
    bot = msg.bot

    try:
        async with AsyncSessionLocal() as session:
            user = await user_service.get_or_create(session=session, tg_id=tg_id)

            item_dict = await get_item_info(url)

            photo_url = item_dict.pop("photo_url")
            photo_bytes = await photo_downloader.download_photo(photo_url)

            item = await item_service.get(item_dict, session=session)

            if not item:
                item = item_service.create(item_dict)

            item.users.append(user)

            await item_service.save(item, session=session)

        await msg.answer(text="Товар добавлен")

        await msg.answer(text=messages.item_info.format(
                title=item.title,
                origin_url=item.origin_url,
                price=item.price
            ),
            parse_mode="Markdown",
            disable_web_page_preview=True)

        input_file = types.input_file.URLInputFile(photo_url)
        sent_msg = await bot.send_photo(chat_id=msg.chat.id, photo=input_file)

        # Получаем ID изображения
        photo_tg_id = sent_msg.photo[-1].file_id  # Получаем наибольшее качество

        item.photo_tg_id = photo_tg_id

        async with AsyncSessionLocal() as session:
            await item_service.save(item, session=session)


    except UrlError as e:
        await msg.answer(text=str(e))

    except ParserError:
        await msg.answer(text=errors.get_item_info_error)

    except PhotoDownloaderError:
        pass

    except DBDublicateError:
        await msg.answer(text=errors.item_dublicate_error)

    except DBError:
        await msg.answer(text=errors.service_unavailable_error)
