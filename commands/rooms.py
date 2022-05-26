from rooms import rooms_service
from users import users_service


def create_room(db, user_id, name, password):
    with db:
        find_room = rooms_service.get_room_by_name(db.cursor(), name)
        if find_room is None:
            rooms_service.create_room(db.cursor(), user_id, name, password)
        elif find_room is not None:
            print("Room with this name already exists. Choose other name.")


def delete_room(db, user_id, room_id):
    with db:
        room = rooms_service.get_room(db.cursor(), room_id)
        if room is None:
            print("Wrong room id!")
            return
        if room.owner != user_id:
            print("You are not owner of the room")
            return

        rooms_service.delete_room_by_id(db.cursor(), room_id)


def list_rooms(db, filter=None):
    with db:
        rooms_list = []
        for room in rooms_service.get_all_rooms(db.cursor()):
            user_list = []
            joined_users = rooms_service.get_all_joined_users(db.cursor(), room.id)
            room_owner = users_service.get_user(db.cursor(), room.owner)
            topic = rooms_service.get_topic(db.cursor(), room.id)
            for user_id in joined_users:
                user_name = users_service.get_user(db.cursor(), user_id)
                user_list.append(user_name.login)
            if filter is None:
                rooms_list.append(
                    [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
            elif filter in user_list:
                rooms_list.append(
                    [room.id, room.name, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
        return rooms_list


def show_room(db, user_id, room_id):
    with db:
        rooms_list = []
        room = rooms_service.get_room(db.cursor(), room_id)
        joined_users = rooms_service.get_all_joined_users(db.cursor(), room_id)
        room_topic = rooms_service.get_topic(db.cursor(), room_id)
        room_owner = users_service.get_user(db.cursor(), room.owner)
        if user_id in joined_users:
            user_list = []
            for room_user_id in joined_users:
                user_name = users_service.get_user(db.cursor(), room_user_id)
                user_list.append(user_name.login)
            rooms_list.append([room.id, room.name, room_topic.topic, room_topic.topic_dsc, user_list, room_owner.login])
            return rooms_list
        else:
            return None


def rating_of_room(db, room_id):
    with db:
        users_ratings = []
        joined_users = rooms_service.get_all_joined_users(db.cursor(), room_id)
        for user_login in joined_users:
            rating = rooms_service.get_rating(db.cursor(), user_login, room_id)
            users_ratings.append([users_service.get_user(db.cursor(), user_login).login, rating[3]])
        return users_ratings


def join_room(db, user_id, room_id, password):
    with db:
        if not rooms_service.join_room(db.cursor(), user_id, room_id, password):
            print("Wrong room/password or you are already in this room")


def leave_room(db, user_id, room_id):
    with db:
        if not rooms_service.leave_room(db.cursor(), user_id, room_id):
            print("You are not in this room or such room doesn't exist")


def change_topic(db, user_id, room_id, topic, desc):
    with db:
        if not rooms_service.update_room(db.cursor(), user_id, room_id, topic, desc):
            print("Room doesn't exist or you are not the owner")


def change_pass(db, user_id, room_id, password):
    with db:
        if not rooms_service.update_room(db.cursor(), user_id, room_id, topic=None, desc=None, password=password):
            print("Room doesn't exist or you are not the owner")


def remove_topic(db, user_id, room_id):
    with db:
        if not rooms_service.update_room(db.cursor(), user_id, room_id):
            print("Room doesn't exist or you are not the owner")


def rate_topic(db, user_id, room_id, rate):
    with db:
        if not rooms_service.update_rating_of_room(db.cursor(), user_id, room_id, rate):
            print("You are not in the room, entered not allowed rating or topic is not set")
