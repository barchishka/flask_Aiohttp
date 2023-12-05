# Импорты ниже требуются для создания моделей и работой с БД
from __future__ import annotations

import datetime
import os
from typing import Annotated
from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)  # импорт фабрики асинхронных движков и сессий.
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship  # создание сессии подключения

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)


intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'owners'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": int(self.registration_time.timestamp()),
        }


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id: Mapped[intpk]
    header: Mapped[str]
    desc: Mapped[str | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey('owners.id', ondelete='CASCADE'))
    owner = relationship(User, cascade='all, delete', backref='advertisements')
