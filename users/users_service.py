import re
from typing import List

import bcrypt

from database.database import Database
from database.users_model import User

LOGIN_RE = r'^[a-zA-Z0-9]+$'


def validate_login(login: str):
    if not len(login) > 3:
        return False

    return re.match(LOGIN_RE, login) is not None


def validate_password(password):
    return len(password) > 4


def has_user(db: Database, login: str):
    return db.find_in_db('users', 'login', login.lower()) is not None


def login(db: Database, login: str, password: str):
    user = db.find_in_db('users', 'login', login.lower())
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return None
    return User(user_id=user[0], login=user[1])


def create_user(db: Database, login: str, password):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    db.put_to_db('users', login=login.lower(), password=password)


def get_all_users(db: Database) -> List[User]:
    return [User(user_id=row[0], login=row[1]) for row in db.find_all_in_db('users')]


def get_user(db: Database, login):
    db_user = db.find_in_db('users', 'login', login.lower())
    if db_user is None:
        return None
    return User(user_id=db_user[0], login=db_user[1])


def remove_user(db: Database, login):
    if db.find_in_db('users', 'login', login.lower()) is not None:
        user = db.find_in_db('users', 'login', login.lower())
        room = db.find_in_db('rooms', 'owner_id', user[0])
        db.remove_from_db('users', 'login', login.lower())
        db.remove_from_db('rooms', 'owner_id', user[0])
        db.remove_from_db('user_room', 'user_id', user[0])
        db.remove_from_db('user_room', 'room_id', room[0])
        print("User has been removed")
    else:
        print("There is no such user")
