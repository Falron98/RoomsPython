from rooms import rooms_service
from users import users_service


def create_room(db, user_id, name, password):
    with db.connect() as conn:
        find_room = rooms_service.get_room_by_name(conn, name)
        if find_room is None:
            rooms_service.create_room(conn, user_id, name, password)
        elif find_room is not None:
            print("Room with this name already exists. Choose other name.")


def delete_room(db, user_id, room_id):
    with db.connect() as conn:
        room = rooms_service.get_room(conn, room_id)
        if room is None:
            print("Wrong room id!")
            return
        if room.owner != user_id:
            print("You are not owner of the room")
            return
        rooms_service.delete_room_by_id(conn, room_id)


def list_rooms(db, filter=None):
    with db.connect() as conn:
        rooms_list = []
        for room in rooms_service.get_all_rooms(conn):
            user_list = []
            joined_users = rooms_service.get_all_joined_users(conn, room.id)
            room_owner = users_service.get_user(conn, room.owner)
            topic = rooms_service.get_topic(conn, room.id)
            for user_id in joined_users:
                user_name = users_service.get_user(conn, user_id)
                user_list.append(user_name.login)
            if filter is None:
                rooms_list.append(
                    [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
            elif filter in user_list:
                rooms_list.append(
                    [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
    return rooms_list


def show_room(db, user_id, room_id):
    with db.connect() as conn:
        rooms_list = []
        room = rooms_service.get_room(conn, room_id)
        joined_users = rooms_service.get_all_joined_users(conn, room_id)
        room_topic = rooms_service.get_topic(conn, room_id)
        room_owner = users_service.get_user(conn, room.owner)
        if user_id in joined_users:
            user_list = []
            for room_user_id in joined_users:
                user_name = users_service.get_user(conn, room_user_id)
                user_list.append(user_name.login)
            rooms_list.append([room.id, room.name, room_topic.topic, room_topic.topic_dsc, user_list, room_owner.login])
            return rooms_list
        else:
            return None


def rating_of_room(db, room_id):
    with db.connect() as conn:
        users_ratings = []
        joined_users = rooms_service.get_all_joined_users(conn, room_id)
        for user_login in joined_users:
            rating = rooms_service.get_rating(conn, user_login, room_id)
            users_ratings.append([users_service.get_user(conn, user_login).login, rating[3]])
    return users_ratings


def join_room(db, user_id, room_id, password):
    with db.connect() as conn:
        if not rooms_service.join_room(conn, user_id, room_id, password):
            print("Wrong room/password or you are already in this room")


def leave_room(db, user_id, room_id):
    with db.connect() as conn:
        if not rooms_service.leave_room(conn, user_id, room_id):
            print("You are not in this room or such room doesn't exist")


def change_topic(db, user_id, room_id, topic, desc):
    with db.connect() as conn:
        if not rooms_service.update_room(conn, user_id, room_id, topic, desc):
            print("Room doesn't exist or you are not the owner")


def change_pass(db, user_id, room_id, password):
    with db.connect() as conn:
        if not rooms_service.update_room(conn, user_id, room_id, topic=None, desc=None, password=password):
            print("Room doesn't exist or you are not the owner")


def remove_topic(db, user_id, room_id):
    with db.connect() as conn:
        if not rooms_service.update_room(conn, user_id, room_id):
            print("Room doesn't exist or you are not the owner")


def rate_topic(db, user_id, room_id, rate):
    with db.connect() as conn:
        if not rooms_service.update_rating_of_room(conn, user_id, room_id, rate):
            print("You are not in the room, entered not allowed rating or topic is not set")
