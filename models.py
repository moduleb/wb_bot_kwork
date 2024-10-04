# modes.py
"""Database Models."""

from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Базовый класс для создания таблиц."""


# Вспомогательная таблица для связи пользователей и товаров
user_item_association = Table(
    "user_item_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    UniqueConstraint("user_id", "item_id", name="uix_user_item")
)


class User(Base):
    """Таблица с пользователями."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger,
                   unique=True,
                   nullable=False,
                   index=True)

    # Связь с товарами
    items = relationship("Item",
                         secondary=user_item_association,
                         back_populates="users")

    def __repr__(self) -> str:
        return f"Class: {self.__class__.__name__}\n\
        id: {self.id}\n\
        tg_id: {self.tg_id}"


class Item(Base):
    """Таблица с товарами."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    origin_url = Column(String,
                        unique=True,
                        nullable=False)
    api_url = Column(String,
                     unique=True,
                     nullable=False)
    market_name = Column(String)

    # Связь с пользователями
    users = relationship("User",
                         secondary=user_item_association,
                         back_populates="items")
