from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from starlette.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models import UserProfile
from backend.app.orm_sender.manager_sqlalchemy import ManagerSQLAlchemy
from backend.app.routes.auth_manager import UserAuthManager
from backend.app.routes.main import MainRouterMIXIN
from backend.app.routes.user.models import *
from backend.app.routes.general_models import GeneralHeadersModel
from backend.app.routes.user.response_models import auth_responses, user_auth_responses, user_create_responses, \
    user_data_responses

user_router = InferringRouter()
user_tags = ["user_router"]


class UserRouterMIXIN(UserAuthManager, MainRouterMIXIN, ManagerSQLAlchemy):

    @staticmethod
    def _get_data_by_response_created(user_profile: UserProfile) -> dict:
        return {
            'id': user_profile.id,
            'name': user_profile.name,
            'lastname': user_profile.lastname,
            'phone_number': user_profile.phone_number,
            'email': user_profile.email,
            'date_birthday': user_profile.date_birthday,
            'restriction_health': user_profile.restriction_health,
            'token_auth': user_profile.token_auth
        }


@cbv(user_router)
class UserAuthRouter(UserRouterMIXIN):
    @user_router.get(
        "/auth/",
        name='auth_user',
        responses=auth_responses,
        description='Авторизация',
        tags=user_tags
    )
    async def get(self, request: Request, response: Response, headers: GeneralHeadersModel = Depends()):
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            if user_profile := await self.authenticate_user(session, None, None, headers.authorization):
                data: dict = self._get_data_by_response_created(user_profile)
                result = self.get_data(data)
                return result

            return self.make_response_by_error()

    @user_router.post(
        "/auth/",
        name='auth_user',
        responses=user_auth_responses,
        description='Аунтефикация',
        tags=user_tags
    )
    async def post(self, request: Request, response: Response, body: UserGETModel):
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            if user_profile := await self.authenticate_user(session, body.phone_number, body.password, None):
                data: dict = self._get_data_by_response_created(user_profile)
                result = self.get_data(data)
                return result

            return self.make_response_by_error()


@cbv(user_router)
class UserRouter(UserRouterMIXIN):

    @user_router.post(
        "/user/",
        name='create_user',
        responses=user_create_responses,
        description='Создание пользователя',
        tags=user_tags
    )
    async def post(self, request: Request, body: UserModel):
        row_data: dict = {
            'password': self.create_hash_password(body.password),
            'phone_number': body.phone_number,
            'token_auth': self.create_access_token()
        }

        data: dict = await self.create_user(row_data)
        result = self.get_data(data)
        return result

    @classmethod
    async def create_user(cls, data: dict) -> dict:
        async with AsyncSession(cls.engine, autoflush=False, expire_on_commit=False) as session:
            if user_profile := await cls._check_phone_number_by_user(session, data['phone_number']):
                return cls._get_data_by_response_created(user_profile)

            user_profile: UserProfile = UserProfile(**data)
            session.add(user_profile)
            await session.commit()
            return cls._get_data_by_response_created(user_profile)

    @staticmethod
    async def _check_phone_number_by_user(session: AsyncSession, phone_number: str) -> UserProfile | None:
        user_profile_select = await session.execute(select(UserProfile).filter_by(phone_number=phone_number))
        if user_profile := user_profile_select.scalars().first():
            return user_profile

        return None


@cbv(user_router)
class UserRouter(UserRouterMIXIN):
    @user_router.post(
        "/user_data/",
        name='create_user_data',
        responses=user_data_responses,
        description='Дополнение данных пользователя',
        tags=user_tags
    )
    async def post(self, request: Request, body: UserDataModel, headers: GeneralHeadersModel = Depends()):
        row_data: dict = {
            'name': body.name,
            'lastname': body.lastname,
            'date_birthday': body.date_birthday,
            'restriction_health': body.restriction_health,
            'email': body.email if body.email else '',
            'token': headers.authorization
        }
        if data := await self.create_user_data(row_data):
            result = self.get_data(data)
            return result

        return self.make_response_by_error()

    async def create_user_data(self, data: dict):
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            user_profile: UserProfile = await self._get_user_by_token(session, data['token'])
            if not user_profile:
                return None

            user_profile.name = data['name']
            user_profile.lastname = data['lastname']
            user_profile.email = data['email']
            user_profile.date_birthday = data['date_birthday']
            user_profile.restriction_health = data['restriction_health']
            await session.commit()

            return self._get_data_by_response_created(user_profile)

    @staticmethod
    async def _get_user_by_token(session: AsyncSession, token: str) -> UserProfile | None:
        user_profile_select = await session.execute(select(UserProfile).filter_by(token_auth=token))
        if user_profile := user_profile_select.scalars().first():
            return user_profile

        return None
