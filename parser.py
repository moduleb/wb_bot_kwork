import logging
from urllib.parse import urlparse

import requests
from requests.exceptions import HTTPError, RequestException

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Исключение для ошибок парсинга данных."""


class UrlError(ParserError):
    """Ошибки url."""


def get_item_info(origin_url: str) -> dict:
    base_url = "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={item_id}"
    _item_id = _get_item_id(origin_url)
    api_url = base_url.format(item_id=_item_id)
    _data = _get_data(api_url)
    price = _get_price(_data)
    title = _get_title(_data)
    return {
        "price": price,
        "title": title,
        "origin_url": origin_url,
        "api_url": api_url
    }


def _get_item_id(url: str) -> int:
    try:
        result = urlparse(url)
        if result.scheme != "https" or result.netloc != "www.wildberries.ru":
            msg = "Ссылка должна начинаться с https://www.wildberries.ru/"
            raise UrlError(msg)

        path_segments = result.path.split("/")
        if len(path_segments) <= 2:
            msg = "URL не является ссылкой на конкретный товар"
            raise UrlError(msg)

        return int(path_segments[2])

    except (ValueError, IndexError) as e:
        msg = "Неправильный формат id"
        raise ParserError(msg) from e


def _get_data(api_url: str) -> dict:

    try:
        response = requests.get(url=api_url, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP

        result = response.json()  # Попытка преобразовать ответ в JSON

        if not result or "data" not in result:
            msg = "Ответ от API Wildberries не содержит данных"
            raise ValueError(msg)

        return result

    except (HTTPError, RequestException) as e:
        logger.exception("Ошибка при получении данных с API")
        raise ParserError from e

    except ValueError as e:
        logger.exception("Ошибка в данных, полученных от API Wildberries")
        raise ParserError from e

    except Exception as e:
        logger.exception("Неизвестная ошибка")
        raise ParserError from e


def _get_price(data: dict) -> int:

    try:
        price = data["data"]["products"][0]["sizes"][0]["price"]["total"]

        if price <= 0:
            msg = "Полученный price <= 0: %s", price
            logger.exception(msg)
            raise ValueError(msg)

        return int(price) // 100  # Возвращаем цену, если она больше 0

    except KeyError as e:
        logger.exception("Ошибка в полученных данных от wb. В 'data' отсутствует ключ 'price'")
        raise ParserError from e

    except IndexError as e:  # формат данных в словаре не совпадает с ожидаемым
        logger.exception("Ошибка в полученных данных от wb. Формат 'data' не соответсвует ожидаемому")
        raise ParserError from e

    except Exception as e:
        logger.exception("Неизвестная ошибка при получении 'price'")
        raise ParserError from e


def _get_title(data: dict) -> str:
    try:
        return data["data"]["products"][0]["name"]

    except KeyError as e:
        logger.exception('Ошибка в полученных данных от wb. Отсутствует ключ: data["data"]["products"][0]["name"]')
        raise ParserError from e
