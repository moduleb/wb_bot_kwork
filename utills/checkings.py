from settings import settings


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом.

    Returns:
        True or False

    """

    return user_id in settings.ADMIN_IDS


