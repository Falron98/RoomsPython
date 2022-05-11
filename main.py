import os
import click
import pandas as pd

from database import database
from rooms import rooms_service
from users import users_service


def get_database():
    db = database.get_db(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__name__)
            ), 'database.sqlite')
    )
    return db


def set_user_login(obj, login, password):
    with obj['db']:
        cursor = obj['db'].cursor()
        user = users_service.login(cursor, login, password)
        if user is None:
            print("Wrong credentials!")
            exit(1)

        obj['user'] = user


@click.group()
@click.pass_context
def run_application(ctx):
    ctx.obj = {'db': get_database()}


@run_application.command('initialize-db', help="Recreate DB")
@click.pass_obj
def clear_db(obj):
    database.initialize_db(obj['db'])


@run_application.group('login', help="Login as existing user")
@click.option("--login", required=True, help="Login of account you want to log in")
@click.password_option()
@click.pass_obj
def login(obj, login, password):
    set_user_login(obj, login, password)


@login.command('remove_user', help="Remove user from database")
@click.option("--user", required=True)
@click.pass_obj
def remove_user(obj, user):
    db = obj['db']
    with obj['db']:
        users_service.remove_user(db.cursor(), user)


@login.command('create_room', help="Create new room")
@click.password_option()
@click.pass_obj
def create_room(obj, password):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        find_room = rooms_service.get_room_by_owner(db.cursor(), user.user_id)
        if find_room is None:
            rooms_service.create_room(db.cursor(), user.user_id, password)
        elif find_room is not None:
            print("You already own a room. Delete it first, to create one.")


@login.command('delete_room', help="Delete existing room from database")
@click.option("--room_id", required=True, help="Id of room you want to delete")
@click.pass_obj
def delete_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        room = rooms_service.get_room(db, room_id)
        if room is None:
            print("Wrong room id!")
            return
        if room.owner != user.user_id:
            print("You are not owner of the room")
            return

        rooms_service.delete_room_by_id(db, room_id)


@login.command('list_users', help="Shows all existing users in database")
@click.option('--filter', help="Filters users by given characters")
@click.pass_obj
def list_users(obj, filter=None):
    db = obj['db']
    with obj['db']:
        users_list = []
        for user in users_service.get_all_users(db.cursor()):
            if filter is None:
                users_list.append([user.user_id, user.login])
            elif user.login.find(filter) > -1:
                users_list.append([user.user_id, user.login])
        df = pd.DataFrame(users_list, columns=['ID', 'Login'])
        print(df)


@login.command('list_rooms', help="Shows all existing rooms in database")
@click.option('--filter', help="Shows all rooms to which the given user belongs")
@click.pass_obj
def list_rooms(obj, filter=None):
    db = obj['db']
    user = obj['user']
    with obj['db']:
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
                rooms_list.append([room.id, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
            elif filter in user_list:
                rooms_list.append([room.id, topic.topic, topic.topic_dsc, sorted(user_list), room_owner.login])
        df = pd.DataFrame(rooms_list, columns=['ID', 'Topic', 'Description', 'Users in room', 'Owner'])
        print(df)


@login.command('show_room', help="Show existing room")
@click.option('--room_id', required=True, help="Id of room you want to show")
@click.pass_obj
def show_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        rooms_list = []
        users_ratings = []
        room = rooms_service.get_room(db.cursor(), room_id)
        joined_users = rooms_service.get_all_joined_users(db.cursor(), room_id)
        room_topic = rooms_service.get_topic(db.cursor(), room_id)
        if user.user_id in joined_users:
            user_list = []
            room_owner = users_service.get_user(db.cursor(), room.owner)
            for user_id in joined_users:
                user_name = users_service.get_user(db.cursor(), user_id)
                user_list.append(user_name.login)
            rooms_list.append([room.id, room_topic.topic, room_topic.topic_dsc, user_list, room_owner.login])
            df = pd.DataFrame(rooms_list, columns=['ID', 'Topic', 'Description', 'Users in room', 'Owner'])
            print(df)
            for user_login in joined_users:
                rating = rooms_service.get_rating(db.cursor(), user_login, room_id)
                users_ratings.append([users_service.get_user(db.cursor(), user_login).login, rating[3]])
            df = pd.DataFrame(users_ratings, columns=['User', 'Rating of Topic'])
            print(df)
        else:
            print("You are not in this room")


@login.command('join_room', help="Join to existing room")
@click.option('--room_id', help="Id of room you want to join")
@click.password_option()
@click.pass_obj
def join_room(obj, room_id, password):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        if not rooms_service.join_room(db.cursor(), user.user_id, room_id, password):
            print("Wrong room/password or you are already in this room")


@login.command('leave_room', help="Leave room you are in")
@click.option('--room_id', help="Id of room you want to leave")
@click.pass_obj
def leave_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        if not rooms_service.leave_room(db.cursor(), user.user_id, room_id):
            print("You are not in this room or such room doesn't exist")


@login.command('change_topic', help="Change topic of room")
@click.option('--room_id', help="Id of room you want to change topic of")
@click.option('--topic', required=False, help="Name of topic you want to set")
@click.option('--desc', required=False, help="Description of topic you want to set")
@click.pass_obj
def change_topic(obj, room_id, topic, desc):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        if not rooms_service.update_room(db.cursor(), user.user_id, room_id, topic, desc):
            print("Room doesn't exist or you are not the owner")


@login.command('remove_topic', help="Remove topic of room")
@click.option('--room_id', help="Id of room you want to remove topic of")
@click.pass_obj
def remove_topic(obj, room_id):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        if not rooms_service.update_room(db.cursor(), user.user_id, room_id):
            print("Room doesn't exist or you are not the owner")


@login.command('rate_topic', help="Rate existing topic of the room")
@click.option('--room_id', required=True, help="Id of room you want to rate")
@click.option('--rate', required=True, help="Integer of how do you rate topic of the room (allowed ratings: 0, 0.5, "
                                            "1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2")
@click.pass_obj
def rate_topic(obj, room_id, rate):
    db = obj['db']
    user = obj['user']
    with obj['db']:
        if not rooms_service.update_rating_of_room(db.cursor(), user.user_id, room_id, rate):
            print("You are not in the room, entered not allowed rating or topic is not set")


@run_application.command('register', help="Register new user")
@click.password_option()
@click.pass_obj
def register_user(obj, password):
    db = obj['db']
    with obj['db']:
        user_login = input("Login:")
        if not users_service.validate_login(user_login):
            print("Wrong login!")
            return
        if not users_service.validate_password(password):
            print("Wrong password!")
            return

        if users_service.has_user(db.cursor(), user_login):
            print("User exists!")
            return

        users_service.create_user(db.cursor(), user_login, password)


if __name__ == '__main__':
    run_application()
