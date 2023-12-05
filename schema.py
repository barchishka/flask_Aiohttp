from __future__ import annotations

import json
from pydantic import field_validator as validator
from pydantic import ValidationError, BaseModel
from typing import Optional, Type
from aiohttp import web


class CreateUser(BaseModel):
    # Прописываем типы данных для запрашиваемых полей. Поля обязательны, т.к. нет параметра Optional
    name: str
    password: str

    # задаем дополнительные проверки при помощи методов и декоратора validator('model_field_name')
    @validator('name')
    def validate_name(cls, value):
        """
        Проверка на длину имени.
        :param value: str
            Проверяемое значение name.
        :return:
            Проверенное значение
        """

        if len(value) > 100:
            raise ValueError('Name is too big. You have 100 symbols.')
        return value

    @validator('password')
    def validate_password(cls, value):
        """
        Проверка на длину пароля.
        :param value: str
            Проверяемое значение name.
        :return:
            Проверенное значение.
        """

        if len(value) < 8:
            raise ValueError('password is too short')
        if len(value) > 100:
            raise ValueError('password is too big')
        return value


class UpdateUser(BaseModel):
    """Валидация данных при обновлении пользователя. Проверки на тип данных и длину значения"""

    name: Optional[str]
    password: Optional[str]

    @validator('name')
    def validate_name(cls, value):
        """
        Проверка на длину имени.
        :param value: str
            Проверяемое значение name.
        :return:
            Проверенное значение
        """
        if len(value) > 100:
            raise ValueError('Name is too big. You have 100 symbols.')
        return value

    @validator('password')
    def validate_password(cls, value):
        """
        Проверка на длину пароля.
          :param value: str
              Проверяемое значение name.
          :return:
              Проверенное значение.
        """
        if len(value) < 8:
            raise ValueError('password is too short')
        if len(value) > 100:
            raise ValueError('password is too big')
        return value


class CreateAdvertisement(BaseModel):
    """Валидация данных при создании объявления."""

    header: str
    desc: Optional[str]
    owner_id: int


class UpdateAdvertisement(BaseModel):
    """Валидация данных при обновлении объявления."""

    header: str
    desc: Optional[str]


def validate(
        json_data: dict,
        model_class: Type[CreateUser] | Type[UpdateUser] | Type[CreateAdvertisement] | Type[UpdateAdvertisement],
):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)

    except ValidationError as error:
        raise web.HTTPBadRequest(
            text=json.dumps({'error': error.errors()}),
            content_type='application/json'
        )