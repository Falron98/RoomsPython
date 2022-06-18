from sqlalchemy.ext.asyncio import AsyncSession

from rooms import rooms_service
from users import users_service


async def create_room(db: AsyncSession, user_id, name, password):
    find_room = await rooms_service.get_room_by_name(db, name)
    if find_room is None:
        await rooms_service.create_room(db, user_id, name, password)
    elif find_room is not None:
        print("Room with this name already exists. Choose other name.")


async def delete_room(db: AsyncSession, user_id, room_id):
    room = await rooms_service.get_room(db, room_id)
    if room is None:
        print("Wrong room id!")
        return
    if room.owner != user_id:
        print("You are not owner of the room")
        return

    await rooms_service.delete_room_by_id(db, room_id)


async def list_rooms(db: AsyncSession, filter=None):
    rooms_list = []
    rooms_db = await rooms_service.get_all_rooms(db)
    for room in rooms_db:
        user_list = []
        joined_users = await rooms_service.get_all_joined_users(db, room.id)
        room_owner = await users_service.get_user(db, room.owner)
        topic = await rooms_service.get_topic(db, room.id)
        for user_id in joined_users:
            user_name = await users_service.get_user(db, user_id)
            user_list.append(user_name.login)
        if filter is None:
            rooms_list.append(
                [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
        elif filter in user_list:
            rooms_list.append(
                [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
    return rooms_list


async def show_room(db: AsyncSession, user_id, room_id):
    rooms_list = []
    room = await rooms_service.get_room(db, room_id)
    joined_users = await rooms_service.get_all_joined_users(db, room_id)
    room_topic = await rooms_service.get_topic(db, room_id)
    room_owner = await users_service.get_user(db, room.owner)
    if user_id in joined_users:
        user_list = []
        for room_user_id in joined_users:
            user_name = await users_service.get_user(db, room_user_id)
            user_list.append(user_name.login)
        rooms_list.append([room.id, room.name, room_topic.topic, room_topic.topic_dsc, user_list, room_owner.login])
        return rooms_list
    else:
        return None


async def rating_of_room(db: AsyncSession, room_id):
    users_ratings = []
    joined_users = await rooms_service.get_all_joined_users(db, room_id)
    for user_login in joined_users:
        rating = await rooms_service.get_rating(db, user_login, room_id)
        user = await users_service.get_user(db, user_login)
        users_ratings.append([user.login, rating.rating])
    return users_ratings


async def join_room(db: AsyncSession, user_id, room_id, password):
    check = await rooms_service.join_room(db, user_id, room_id, password)
    if not check:
        print("Wrong room/password or you are already in this room")
        return 'err_1'


async def leave_room(db: AsyncSession, user_id, room_id):
    if not await rooms_service.leave_room(db, user_id, room_id):
        print("You are not in this room or such room doesn't exist")


async def change_topic(db: AsyncSession, user_id, room_id, topic, desc):
    if not await rooms_service.update_room(db, user_id, room_id, topic, desc):
        print("Room doesn't exist or you are not the owner")


async def change_pass(db: AsyncSession, user_id, room_id, password):
    if not await rooms_service.update_room(db, user_id, room_id, topic=None, desc=None, password=password):
        print("Room doesn't exist or you are not the owner")


async def remove_topic(db: AsyncSession, user_id, room_id):
    if not await rooms_service.update_room(db, user_id, room_id):
        print("Room doesn't exist or you are not the owner")


async def rate_topic(db: AsyncSession, user_id, room_id, rate):
    if not await rooms_service.update_rating_of_room(db, user_id, room_id, rate):
        print("You are not in the room, entered not allowed rating or topic is not set")
