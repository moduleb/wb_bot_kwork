import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.input_file import URLInputFile
from aiohttp.client_exceptions import ClientResponseError
from aiogram.exceptions import TelegramNetworkError, TelegramForbiddenError

logger = logging.getLogger(__name__)


KeyboardVarkup = ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove


class SendPhotoError(Exception):
    """Ошибка при отравке сообщения."""


async def _send_photo(bot: Bot,
                      chat_id: int,
                      text: str,
                      photo: str | URLInputFile,
                      reply_markup: KeyboardVarkup) -> str:

    sent_msg = await bot.send_photo(chat_id=chat_id,
                                     photo=photo,
                                     caption=text,
                                     parse_mode="Markdown",
                                    reply_markup=reply_markup)

    return sent_msg.photo[-1].file_id

# --------------------------------------------------------------------------------------


async def send_photo_by_photo_id(bot: Bot,
                                 chat_id: int,
                                 text: str,
                                 photo_id: str,
                                 photo_url: str,
                                 reply_markup: KeyboardVarkup
                                 ) -> str | None:

    try:
        return await _send_photo(bot=bot,
                                 chat_id=chat_id,
                                 text=text,
                                 photo=photo_id,
                                 reply_markup=reply_markup)

    except TelegramBadRequest as e:
        logger.warning("Ошибка при отправке изображения по photo_id: %s.\n"
                       "Попытка отправить по photo_url и обновить photo_id. "
                       "Error: %s", photo_id, str(e))

        return await send_photo_by_photo_url(bot=bot,
                                              chat_id=chat_id,
                                              text=text,
                                              photo_url=photo_url,
                                              reply_markup=reply_markup)

# --------------------------------------------------------------------------------------


async def send_photo_by_photo_url(bot: Bot,
                                   chat_id: int,
                                   text: str,
                                   photo_url: str,
                                   reply_markup: KeyboardVarkup
                                   ) -> str:

    try:
        return await _send_photo(bot=bot,
                                 chat_id=chat_id,
                                 text=text,
                                 photo=URLInputFile(photo_url),
                                 reply_markup=reply_markup)

    except (ClientResponseError, TelegramNetworkError) as e:
        msg = ("Невозможно загрузить изображение по photo_url: %s\n"
               "Error: %s") % (photo_url, str(e))
        logger.warning(msg)

        raise SendPhotoError(msg) from e

    except TelegramBadRequest as e:
        msg = ("Ошибка при отправке изображения по photo_url: %s.\n"
                "Error: %s") % (photo_url, str(e))
        logger.warning(msg)
        raise SendPhotoError(msg) from e

    except TelegramForbiddenError as e:
        msg = "Не удалось отправить сообщение, пользователь заблокировал бота."
        logger.info(msg)
        raise SendPhotoError(msg) from e
