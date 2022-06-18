import re
from typing import List

import bcrypt
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.Alchemymodels import UserDB
from database.users_model import User

LOGIN_RE = r'^[a-zA-Z0-9]+$'


def validate_login(user_login: str):
    if not len(user_login) > 3:
        return False

    return re.match(LOGIN_RE, user_login) is not None


def validate_password(password: str):
    return len(password) > 4


async def has_user(db: AsyncSession, user_login: str):
    user = await db.execute(select(UserDB).where(UserDB.login == user_login))
    return len(user.scalars().all()) > 0


async def login(db: AsyncSession, user_login: str, password: str):
    user = await db.execute(select(UserDB).where(UserDB.login == user_login))
    user = user.scalars().first()
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return None
    return User(user_id=user.user_id, login=user.login)


async def create_user(db: AsyncSession, user_login: str, password: str):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    await db.execute(insert(UserDB).values(login=user_login, password=password))


async def get_all_users(db: AsyncSession) -> List[User]:
    users = await db.execute(select(UserDB))
    users = users.scalars().all()
    return [User(user_id=row.user_id, login=row.login) for row in users]


async def get_user(db: AsyncSession, user_id: int):
    db_user = await db.execute(select(UserDB).where(UserDB.user_id == user_id))
    db_user = db_user.scalars().first()
    if db_user is None:
        return None
    return User(user_id=db_user.user_id, login=db_user.login)


async def remove_user(db: AsyncSession, user_login):
    await db.execute("DELETE FROM users WHERE login = ?", (user_login, ))
