import logging
from urllib.parse import urlparse

import aiohttp
from utills.parser_photo import get_photo_url

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Исключение для ошибок парсинга данных."""


class UrlError(ParserError):
    """Ошибки url."""


async def get_item_info(origin_url: str) -> dict:
    base_url = "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={item_id}"

    _item_id = _get_item_id(origin_url)
    photo_url = get_photo_url(_item_id)
    api_url = base_url.format(item_id=_item_id)
    _rqquest_data = await _get_data(api_url)

    item_info_dict = _extract_product_info(_rqquest_data)

    item_info_dict["photo_url"] = photo_url
    item_info_dict["origin_url"] = origin_url
    item_info_dict["api_url"] = api_url

    return item_info_dict


def _get_item_id(url: str) -> int:
    """Извлекает item_id из origin_url."""
    result = urlparse(url)

    if result.scheme != "https" or result.netloc != "www.wildberries.ru":
        msg = "Ссылка должна начинаться с https://www.wildberries.ru/"
        logger.debug(msg)
        raise UrlError(msg)

    path_segments = result.path.split("/")
    if len(path_segments) < 3:
        msg = "URL не является ссылкой на конкретный товар"
        logger.debug(msg)
        raise UrlError(msg)

    item_id = path_segments[2]

    try:
        return int(item_id)

    except ValueError as e:
        msg = "Полученный 'item_id' не является числом"
        logger.exception(msg)
        raise ParserError(msg) from e


async def _get_data(api_url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session, session.get(api_url) as response:
            response.raise_for_status()
            result = await response.json()

        if result and "data" in result:
            return result

        msg = "Ответ от API Wildberries не содержит данных"
        logger.exception(msg)
        raise ParserError(msg)

    # Ошибка при преобразовывании в JSON
    except aiohttp.ContentTypeError as e:
        msg = "Ответ от API не является корректным JSON"
        logger.exception(msg)
        raise ParserError(msg) from e

    # Общая ошибка подключения
    except aiohttp.ClientError as e:
        msg = "Ошибка при получении данных с API"
        logger.exception(msg)
        raise ParserError(msg) from e


def _extract_product_info(data: dict) -> dict:

    try:
        product_data = data["data"]["products"][0]
        # import pdb; pdb.set_trace()

        return {
            "price": _get_price(product_data),
            "title": product_data["name"],
        }

    except (IndexError, KeyError) as e:
        msg = "Ошибка в полученных данных от wb. Формат 'data' не соответсвует ожидаемомy"
        logger.exception(msg)
        raise ParserError(msg) from e


def _get_price(product_data: dict) -> float:
    """Извлекаем price."""
    # Если размера нет, то не будет ключа 'price'
    # Поэтому перебираем все размеры, пока не найдем 'price'
    price = 0
    if sizes := product_data.get("sizes"):
        for size in sizes:
            if prices := size.get("price"):
                price = prices.get("total")
                if price > 0:
                    break

    # price = product_data["sizes"][0]["price"]["total"]

    # if price <= 0:
    #     msg = "Полученный price <= 0: %s", price
    #     logger.exception(msg)
    #     raise ParserError(msg)

    try:
        return float(price) / 100  # Возвращаем цену

    except ValueError as e:
        msg = "Полученный 'price' не является числом"
        logger.exception(msg)
        raise ParserError(msg) from e
