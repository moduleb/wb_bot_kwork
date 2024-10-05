
import io
import logging

import aiohttp

logger = logging.getLogger(__name__)


class PhotoDownloaderError(Exception):
    pass


async def download_photo(photo_url: str) -> io.BytesIO:
    try:
        async with aiohttp.ClientSession() as session,\
            session.get(photo_url) as response:

            response.raise_for_status()

            content = await response.read()

            if content:
                return io.BytesIO(content)

            msg = "Ошибка при скачивании изображения: ответ от сервера не содержит данных"
            logger.exception(msg)
            raise PhotoDownloaderError(msg)

    # Общая ошибка подключения
    except aiohttp.ClientError as e:
        msg = "Ошибка при скачивании изображения"
        logger.exception(msg)
        raise PhotoDownloaderError(msg) from e
