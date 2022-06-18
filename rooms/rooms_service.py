from typing import List, Union

import bcrypt
from sqlalchemy import select, and_, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.Alchemymodels import RoomDB, UserRoomDB, TopicDB
from database.rooms_model import Room, Topic

RATING_RE = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2]


async def create_room(db: AsyncSession, owner_id: int, name: str, password: str):
    salt = bcrypt.gensalt()
    hashed_psw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    await db.execute(insert(RoomDB).values(name=name, password=hashed_psw, owner_id=owner_id))
    out = await db.execute(select(RoomDB).where(RoomDB.name == name))
    out = out.scalars().first()
    await db.execute(insert(TopicDB).values(room_id=out.room_id, topic='None', topic_dsc='None'))
    out2 = await db.execute(select(TopicDB).where(TopicDB.room_id == out.room_id))
    out2 = out2.scalars().first()
    await db.execute(update(RoomDB).where(RoomDB.room_id == out.room_id).values(topic_id=out2.topic_id))
    if not await join_room(db, owner_id, out.room_id, password):
        raise Exception("Owner could not join the room!")



async def get_room(db: AsyncSession, room_id: int):
    db_room = await db.execute(select(RoomDB).where(RoomDB.room_id == room_id))
    db_room = db_room.scalars().first()
    if db_room is None:
        return None
    return Room(id=db_room.room_id, name=db_room.name, password=db_room.password, owner=db_room.owner_id)


async def get_room_by_name(db: AsyncSession, name: str):
    db_room = await db.execute(select(RoomDB).where(RoomDB.name == name))
    db_room = db_room.scalars().first()
    if db_room is None:
        return None
    return Room(id=db_room.room_id, name=db_room.name, password=db_room.password, owner=db_room.owner_id)


async def delete_room_by_id(db: AsyncSession, room_id: int):
    await db.execute(delete(UserRoomDB).where(UserRoomDB.room_id == room_id))
    await db.execute(delete(RoomDB).where(RoomDB.room_id == room_id))


async def join_room(db: AsyncSession, user_id: int, room_id: int, password: str) -> bool:
    room = await get_room(db, room_id)
    if room is None:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
        return False
    await db.execute(insert(UserRoomDB).values(user_id=user_id, room_id=room_id))
    await db.commit()
    return True


async def get_topic(db: AsyncSession, room_id: int) -> Union[Topic, None]:
    topic = await db.execute(select(TopicDB).where(TopicDB.room_id == room_id))
    topic = topic.scalars().first()
    if topic is None:
        return None
    return Topic(id=topic.topic_id, room_id=topic.room_id, topic=topic.topic, topic_dsc=topic.topic_dsc)


async def get_topic_by_id(db: AsyncSession, topic_id: int) -> Union[Topic, None]:
    topic = await db.execute(select(TopicDB).where(TopicDB.topic_id == topic_id))
    topic = topic.scalars().first()
    if topic is None:
        return None

    return Topic(id=topic.topic_id, room_id=topic.room_id, topic=topic.topic, topic_dsc=topic.topic_dsc)


async def leave_room(db: AsyncSession, user_id: int, room_id: int) -> bool:
    room = await get_room(db, room_id)
    joined_users = await get_all_joined_users(db, room_id)
    if room is None:
        return False
    if user_id not in joined_users:
        return False
    if user_id is room.owner:
        return False
    await db.execute(delete(UserRoomDB).where(and_(UserRoomDB.user_id == user_id, UserRoomDB.room_id == room_id)))
    await db.commit()
    return True


async def update_room(db: AsyncSession, user_id: id, room_id: int, topic=None, desc=None, password=None) -> bool:
    room = await get_room(db, room_id)
    if room is None:
        return False
    if user_id != room.owner:
        return False
    if topic is not None:
        await db.execute(update(TopicDB).where(TopicDB.room_id == room_id).values(topic=topic, topic_dsc='None'))
        await db.execute(update(UserRoomDB).where(UserRoomDB.room_id == room_id).values(rating=None))
    if desc is not None:
        await db.execute(update(TopicDB).where(TopicDB.room_id == room_id).values(topic_dsc=desc))
    if password is not None:
        salt = bcrypt.gensalt()
        hashed_psw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        await db.execute(update(RoomDB).where(RoomDB.room_id == room_id).values(password=hashed_psw))
    return True


async def update_rating_of_room(db: AsyncSession, user_id: int, room_id: int, rating: float) -> bool:
    room = await get_room(db, room_id)
    joined_users = await get_all_joined_users(db, room_id)
    room_topic = await db.execute(select(TopicDB).where(TopicDB.room_id == room_id))
    room_topic = room_topic.scalars().first()
    if room is None:
        return False
    elif float(rating) not in RATING_RE:
        return False
    elif user_id not in joined_users:
        return False
    elif room_topic.topic is None:
        return False
    await db.execute(update(UserRoomDB).where(and_(UserRoomDB.user_id == user_id, UserRoomDB.room_id == room_id)).values(rating=rating))
    return True


async def get_rating(db: AsyncSession, user_id: int, room_id):
    rating = await db.execute(select(UserRoomDB).where(and_(UserRoomDB.user_id == user_id, UserRoomDB.room_id == room_id
                                                            )))
    rating = rating.scalars().first()
    if rating is None:
        return None

    return rating


async def get_all_rooms(db: AsyncSession) -> List[Room]:
    rooms = await db.execute(select(RoomDB))
    rooms = rooms.scalars().all()
    return [Room(id=row.room_id, name=row.name, password=row.password, owner=row.owner_id) for row in rooms]


async def get_all_joined_users(db: AsyncSession, room_id: int):
    user_room_joined = await db.execute(select(UserRoomDB).where(UserRoomDB.room_id == room_id))
    user_room_joined = user_room_joined.scalars().all()
    users_in_room = []
    for row in user_room_joined:
        users_in_room.append(row.user_id)
    return users_in_room
