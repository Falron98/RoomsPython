from typing import List

import bcrypt

from database.database import Database
from database.rooms_model import Room

RATING_RE = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2]


def create_room(db: Database, owner_login: str, password: str):
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    user_credentials = db.find_in_db('users', 'login', owner_login)
    db.put_to_db('rooms', password=password, owner_id=user_credentials[0])
    db_room = db.find_in_db('rooms', 'owner_id', user_credentials[0])
    db.put_to_db('user_room', user_id=user_credentials[0], room_id=db_room[0])
    db.put_to_db('topics', topic='None', topic_dsc='None', room_id=db_room[0])
    db.update_to_db('rooms', 'topic_id', 'room_id', db.find_in_db('topics', 'room_id', db_room[0])[0], db_room[0])


def get_room(db: Database, id: str):
    db_room = db.find_in_db('rooms', 'room_id', id)
    if db_room is None:
        return None
    return Room(id=db_room[0], owner=db_room[2], password=db_room[1], joined_users=get_all_joined_users(db, id),
                topic=db.find_in_db('topics', 'room_id', db_room[0])[1], topic_desc=db.find_in_db('topics', 'room_id', db_room[0])[2])


def delete_room_by_id(db: Database, id: str):
    db.remove_from_db('rooms', 'room_id', id)
    db.remove_from_db('user_room', 'room_id', id)
    db.remove_from_db('topics', 'room_id', id)


def join_room(db: Database, user_id: str, id: str, password: str) -> bool:
    room = get_room(db, id)
    if room is None:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
        return False
    if user_id in room.joined_users:
        return False
    db.put_to_db('user_room', user_id=user_id, room_id=id)
    return True


def update_room(db: Database, user: str, id: str, topic=None, desc=None) -> bool:
    room = get_room(db, id)
    if room is None:
        return False
    if user != room.owner:
        return False
    if topic is not None:
        db.update_to_db('topics', 'topic', 'room_id', topic, id)
        db.update_to_db('topics', 'topic_dsc', 'room_id', None, id)
        db.update_to_db('user_room', 'topic_rating', 'room_id', None, id)
    if desc is not None:
        db.update_to_db('topics', 'topic_dsc', 'room_id', desc, id)
    return True


def update_rating_of_room(db: Database, user: str, id: str, rating: str) -> bool:
    room = get_room(db, id)
    if room is None:
        return False
    if float(rating) not in RATING_RE:
        return False
    if user not in room.joined_users:
        return False
    db.update_to_db_2('user_room', 'topic_rating', 'room_id', 'user_id', rating, id, user)
    return True


def get_all_rooms(db: Database) -> List[Room]:
    return [Room(id=row[0], owner=row[2], password=row[1], joined_users=get_all_joined_users(db, row[0]),
                 topic=db.find_in_db('topics', 'room_id', row[0])[1], topic_desc=db.find_in_db('topics', 'room_id', row[0])[2]) for row in db.find_all_in_db('rooms')]


def get_all_joined_users(db: Database, id: str):
    user_room_joined = []
    for db_room_join in db.find_all_in_db('user_room', "WHERE room_id = " + str(id)):
        user_room_joined.append(db_room_join[0])
    return user_room_joined
