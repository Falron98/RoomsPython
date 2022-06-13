from typing import List, Union

import bcrypt

from database.rooms_model import Room, Topic

RATING_RE = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2]


def create_room(db, owner_id: int, name: str, password: str):
    salt = bcrypt.gensalt()
    hashed_psw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    with db.begin():
        out = db.execute("INSERT INTO rooms (owner_id, name, password) VALUES (?, ?, ?) RETURNING room_id", (owner_id, name, hashed_psw)).fetchone()[0]
        if not join_room(db, owner_id, out, password):
            raise Exception("Owner could not join the room!")
        db.execute("INSERT INTO topics (room_id, topic, topic_dsc) VALUES (?, ?, ?)", (out, 'None', 'None'))


def get_room(db, room_id: int):
    with db.begin():
        db_room = db.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
    if db_room is None:
        return None
    return Room(id=db_room[0], name=db_room[1], password=db_room[2], owner=db_room[3])


def get_room_by_name(db, name: int):
    with db.begin():
        db_room = db.execute("SELECT * FROM rooms WHERE name = ?", (name,)).fetchone()
    if db_room is None:
        return None
    return Room(id=db_room[0], name=db_room[1], password=db_room[2], owner=db_room[3] )


def delete_room_by_id(db, room_id: int):
    with db.begin():
        db.execute("DELETE FROM user_room WHERE room_id=?", (room_id,))
        db.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))


def join_room(db, user_id: int, room_id: int, password: str) -> bool:
    with db.begin():
        room = get_room(db, room_id)
        if room is None:
            return False
        if not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
            return False
        db.execute("INSERT INTO user_room (user_id, room_id) VALUES (?, ?)", (user_id, room_id))
    return True


def get_topic(db, room_id: int) -> Union[Topic, None]:
    with db.begin():
        topic = db.execute("SELECT * FROM topics WHERE room_id = ?", (room_id,)).fetchone()
    if topic is None:
        return None

    return Topic(id=topic[0], room_id=topic[1], topic=topic[2], topic_dsc=topic[3])


def get_topic_by_id(db, topic_id: int) -> Union[Topic, None]:
    with db.begin():
        topic = db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if topic is None:
        return None

    return Topic(id=topic[0], room_id=topic[1], topic=topic[2], topic_dsc=topic[3])


def leave_room(db, user_id: int, room_id: int) -> bool:
    with db.begin():
        room = get_room(db, room_id)
        joined_users = get_all_joined_users(db, room_id)
        if room is None:
            return False
        if user_id not in joined_users:
            print(joined_users)
            return False
        if user_id is room.owner:
            return False
        db.execute("DELETE FROM user_room WHERE user_id = ? AND room_id = ?", (user_id, room_id))
        return True


def update_room(db, user_id: id, room_id: int, topic=None, desc=None, password=None) -> bool:
    with db.begin():
        room = get_room(db, room_id)
        if room is None:
            return False
        if user_id != room.owner:
            return False
        if topic is not None:
            db.execute("UPDATE topics SET topic = ?, topic_dsc = ? WHERE room_id = ?", (topic, 'None', room_id))
            db.execute("UPDATE user_room SET topic_rating = ? WHERE room_id = ?", (None, room_id))
        if desc is not None:
            db.execute("UPDATE topics SET topic_dsc = ? WHERE room_id = ?", (desc, room_id))
        if password is not None:
            salt = bcrypt.gensalt()
            hashed_psw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            db.execute("UPDATE rooms SET password = ? WHERE room_id = ?", (hashed_psw, room_id))
        return True


def update_rating_of_room(db, user_id: int, room_id: int, rating: float) -> bool:
    with db.begin():
        room = get_room(db, room_id)
        joined_users = get_all_joined_users(db, room_id)
        room_topic = db.execute("SELECT * FROM topics WHERE room_id = ?", (room_id,)).fetchone()
        if room is None:
            return False
        elif float(rating) not in RATING_RE:
            return False
        elif user_id not in joined_users:
            return False
        elif room_topic[2] is None:
            return False
        db.execute("UPDATE user_room SET topic_rating = ? WHERE user_id = ? AND room_id = ?", (rating, user_id, room_id))
        return True


def get_rating(db, user_id: int, room_id):
    with db.begin():
        rating = db.execute("SELECT * FROM user_room WHERE user_id = ? AND room_id = ?", (user_id, room_id)).fetchone()
    if rating is None:
        return None

    return rating


def get_all_rooms(db) -> List[Room]:
    with db.begin():
        return [Room(id=row[0], name=row[1], password=row[2], owner=row[3]) for row in db.execute("SELECT * FROM rooms")]


def get_all_joined_users(db, room_id: int):
    with db.begin():
        user_room_joined = db.execute("SELECT * FROM user_room WHERE room_id = ?", (room_id,)).fetchall()
    users_in_room = []
    for row in user_room_joined:
        users_in_room.append(row[1])
    return users_in_room
