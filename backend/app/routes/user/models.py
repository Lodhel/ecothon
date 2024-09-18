from pydantic import BaseModel
from fastapi import Query


class UserModel(BaseModel):
    password: str = Query(..., description="пароль")
    phone_number: str = Query(..., description="номер телефона")


class UserDataModel(BaseModel):
    name: str = Query(..., description="имя пользователя")
    lastname: str = Query(..., description="фамилия пользователя")
    date_birthday: str = Query(..., description="день рождения")
    restriction_health: str = Query(..., description="ограничение по здоровью")
    email: str = Query(default=None, description="эмайл")


class UserGETModel(BaseModel):
    password: str = Query(..., description="пароль")
    phone_number: str = Query(..., description="номер телефона")
