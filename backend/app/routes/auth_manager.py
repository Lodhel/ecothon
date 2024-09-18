from secrets import token_hex

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from passlib.context import CryptContext

from backend.app.models import UserProfile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserAuthManager:

    @staticmethod
    def create_access_token():
        return token_hex(16)

    @staticmethod
    def create_static_password():
        return token_hex(8)

    @classmethod
    async def authenticate_user(
            cls, session: AsyncSession, phone_number: str | None, password: str | None, token_auth: str | None
    ) -> UserProfile | None:
        if not password:
            return await cls.get_userprofile_by_token(session, token_auth)

        userprofile: UserProfile = await cls.get_user(session, phone_number)
        if not userprofile or not cls.verify_password(password, userprofile.password):
            return None
        return userprofile

    @staticmethod
    async def get_user(session: AsyncSession, phone_number: str) -> UserProfile:
        user_select = await session.execute(select(UserProfile).filter_by(phone_number=phone_number))
        return user_select.scalars().first()

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    async def get_userprofile_by_token(session: AsyncSession, token_auth: str) -> UserProfile | None:
        if token_auth:
            user_select = await session.execute(select(UserProfile).filter_by(token_auth=token_auth))
            return user_select.scalars().first()

        return None
