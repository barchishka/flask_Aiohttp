from __future__ import annotations

import json

from models import Session, User, Advertisement, engine, Base
from typing import Type
from aiohttp import web
import bcrypt


async def get_orm_item(item_class: Type[User] | Type[Advertisement], item_id: int, session: Session):
    """
    Функция принимает на вход класс объекта, id объекта и сессию, возвращает запрашиваемый экземпляр класса с нужным id.

    :param item_class: Type[User] | Type[Advertisement]
        Класс объекта, который нужно получить.
    :param item_id: int
        id объекта, который нужно получить.
    :param session: Session
        Сессия для работы с БД.
    :return:
        Экземпляр класса объекта.
    """

    item = await session.get(item_class, item_id)  # получаем из БД запрашиваемый экземпляр класса
    if item is None:  # если не существует, выдаем ошибку "Не найдено".
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'object is not found'}),
                               content_type='application/json')
    return item


def hash_password(password: str):
    """
    Функция для хеширования пароля. Принимает пароль строкового типа.

    :param password: str
        Пароль строкового типа.
    :return:
        Хешированный пароль строкового типа.
    """

    encoded_password = password.encode()
    hashed_password = bcrypt.hashpw(password=encoded_password, salt=bcrypt.gensalt())
    decoded_password = hashed_password.decode()
    return decoded_password


async def orm_context(some_app: web.Application):
    """
    Функция принимает экземпляр класса приложения, подключается к БД, делает миграции,
    по окончании работы закрывает соединение.
    Все, что до слова yield, выполнится на старте работы приложения. Что после - в конце работы приложения.

    :param some_app: web.Application
        экземпляр приложения.
    :return:
        None
    """

    print('START')  # просто текстовая метка.
    async with engine.begin() as connection:  # создаем подключение.
        await connection.run_sync(Base.metadata.create_all)  # делаем миграции, т.е. создаем таблицы в БД.
    yield
    await engine.dispose()  # закрываем соединение.
    print('END')  # просто текстовая метка.


@web.middleware  # обозначаем функцию как middleware.
async def session_middleware(request: web.Request, handler):
    """
    Функция для создания сессии подключения и ее закрытия после получения response.

    :param request:
        Запрос от клиента.
    :param handler:
        Метод-обработчик представления. Асинхронный метод get, post и т.д.
    :return:
        Объект response.
    """

    async with Session() as session:  # создаем сессию
        request['session'] = session  # добавляем в словарь request сессию
        response = await handler(request)  # отправляем запрос к методу представления
        return response