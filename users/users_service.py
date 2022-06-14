import re
from sqlite3 import Cursor
from typing import List

import bcrypt

from database.users_model import User

LOGIN_RE = r'^[a-zA-Z0-9]+$'


def validate_login(user_login: str):
    if not len(user_login) > 3:
        return False

    return re.match(LOGIN_RE, user_login) is not None


def validate_password(password: str):
    return len(password) > 4


def has_user(db: Cursor, user_login: str):
    return len(db.execute("SELECT * FROM users WHERE login = ?", (user_login,)).fetchall()) > 0


def login(db: Cursor, user_login: str, password: str):
    user = db.execute("SELECT * FROM users WHERE login = ?", (user_login,)).fetchone()
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return None
    return User(user_id=user[0], login=user[1])


def create_user(db: Cursor, user_login: str, password: str):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    db.execute("INSERT INTO users (login, password) VALUES (?, ?)", (user_login.lower(), password))


def get_all_users(db: Cursor) -> List[User]:
    return [User(user_id=row[0], login=row[1]) for row in db.execute("SELECT * FROM users ")]


def get_user(db: Cursor, user_id: int):
    db_user = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if db_user is None:
        return None
    return User(user_id=db_user[0], login=db_user[1])


def remove_user(db: Cursor, user_login):
    db.execute("DELETE FROM users WHERE login = ?", (user_login, ))
