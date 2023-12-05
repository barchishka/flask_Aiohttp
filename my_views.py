import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import User, Advertisement
from client_request import get_orm_item, hash_password
from schema import validate, CreateUser, UpdateUser, CreateAdvertisement, UpdateAdvertisement


class UserView(web.View):

    async def get(self):
        """
        Метод get возвращает данные конкретного пользователя.

        :return: dict
            json с данными пользователя
        """

        # сессия хранится в объекте (request['session']), помещена туда при помощи session_middleware.
        user_id = int(self.request.match_info.get('user_id'))  # достаем id из атрибута match_info
        user = await get_orm_item(User, user_id, session=self.request.get('session'))  # получаем пользователя
        response = web.json_response({'user_id': user.id, 'user_name': user.name})  # json с данными пользователя
        return response

    async def post(self):
        """
        Метод POST позволяет создать пользователя и вернуть json с его id.

        :return: dict
            Json с id пользователя.
        """

        user_data = await self.request.json()  # принятые данные из request
        validated_data = validate(json_data=user_data, model_class=CreateUser)  # валидируем данные при помощи
        # написанной ф-и.
        user_password = validated_data.get('user_pass')  # достаем пароль
        hashed_pass = hash_password(user_password)  # хэшируем его.
        validated_data['user_pass'] = hashed_pass  # вставляем обратно в валидированные данные.
        new_user = User(**validated_data)  # создаем нового пользователя
        self.request.get('session').add(new_user)  # Добавляем в сессии. Сессия находится в request['session']
        try:
            await self.request.get('session').commit()  # делаем коммит.
        except IntegrityError:  # если пользователь существует, генерим ошибку.
            raise web.HTTPConflict(text=json.dumps({'status': 'user already exists'}), content_type='application/json')

        return web.json_response({'user_id': new_user.id})  # возвращаем json с данными пользователя.

    async def patch(self):
        """
        Метод PATCH позволяет обновить данные пользователя. Если есть пароль, то метод проведет хэширование.

        :return: dict
            json словарь с id пользователя, чьи данные изменены.
        """

        user_id = int(self.request.match_info.get('user_id'))  # достаем id пользователя.
        user_data = await self.request.json()  # получаем данные из запроса
        user_validated_data = validate(json_data=user_data, model_class=UpdateUser)  # валидируем данные
        if 'user_pass' in user_validated_data:  # если есть пароль в данных, хэшируем его
            user_validated_data['user_pass'] = hash_password(user_validated_data.get('user_pass'))

        # получаем пользователя из БД
        user = await get_orm_item(item_class=User, item_id=user_id, session=self.request['session'])
        for field, value in user_validated_data.items():  # устанавливаем валидные значения пользователю.
            setattr(user, field, value)
        self.request['session'].add(user)  # добавляем данные в БД
        await self.request['session'].commit()  # делаем коммит

        return web.json_response({'user_id': user_id})  # возвращаем json с id.

    async def delete(self):
        """
        Метод DELETE удаляет пользователя, id которого передано в запросе.

        :return: dict
            json словарь со статусом.
        """

        user_id = int(self.request.match_info.get('user_id'))  # достаем id пользователя.
        user = await get_orm_item(item_class=User, item_id=user_id, session=self.request['session'])
        session = self.request['session']
        await session.delete(user)
        await session.commit()
        return web.json_response({'status': 'user is deleted'})


class AdvertisementView(web.View):

    async def get(self):
        """
        Метод GET позволяет получить данные по id объявления.
        :return: json dict
            json с id, заголовком и создателем объявления
        """

        adv_id = int(self.request.match_info.get('advertisement_id'))  # достаем id из атрибута match_info
        # получаем объявление из БД
        adv = await get_orm_item(item_class=Advertisement, item_id=adv_id, session=self.request.get('session'))
        # оформляем в json
        response = web.json_response({'advertisement_id': adv.id, 'header': adv.header, 'owner_id': adv.owner_id})
        return response

    async def post(self):
        """
        Метод POST позволяет создать объявление. Обязательные поля - header, owner_id
        :return: json dict
            json с заголовком объявления.
        """

        adv_data = await self.request.json()  # получаем данные из запроса
        validated_data = validate(json_data=adv_data, model_class=CreateAdvertisement)  # валидируем
        new_adv = Advertisement(**validated_data)  # создаем экземпляр класса Advertisement
        self.request.get('session').add(new_adv)  # добавляем в БД
        await self.request.get('session').commit()  # делаем коммит
        return web.json_response({'advertisement_header': new_adv.header})

    async def patch(self):
        """
        Метод PATCH позволяет обновить объявление.
        :return: json dict
            json  с id  измененного объявления
        """

        adv_id = int(self.request.match_info.get('advertisement_id'))  # достаем id объявления из атрибута match_info
        adv_data = await self.request.json()  # достаем данные из запроса
        validated_data = validate(json_data=adv_data, model_class=UpdateAdvertisement)  # валидируем
        # достаем объект из БД
        adv = await get_orm_item(item_class=Advertisement, item_id=adv_id, session=self.request.get('session'))
        for field, value in validated_data.items():  # устанавливаем новые значения атрибутов объекта
            setattr(adv, field, value)
        self.request.get('session').add(adv)  # добавляем обновленный объект в БД
        await self.request.get('session').commit()  # делаем коммит

        return web.json_response({'adv_id': adv.id})

    async def delete(self):
        """
        Метод DELETE позволяет удалить объявление.
        :return: json dict
            json со статусом удаления.
        """

        adv_id = int(self.request.match_info.get('advertisement_id'))  # достаем id объявления из атрибута match_info
        # достаем объект из БД
        adv = await get_orm_item(item_class=Advertisement, item_id=adv_id, session=self.request.get('session'))
        await self.request.get('session').delete(adv)  # удаляем
        await self.request.get('session').commit()  # делаем коммит

        return web.json_response({'status': f'advertisement {adv_id} is deleted'})