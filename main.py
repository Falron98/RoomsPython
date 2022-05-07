import os
import click

from database import database
from rooms import rooms_service
from users import users_service

@click.group()
@click.pass_context
def run_application(ctx):
    ctx.obj = {'db': get_database()}


@run_application.command("clear-db", help="Recreate DB")
def clear_db():
    db = get_database()
    db.initialize_db()


@run_application.group('login', help="Login as existing user")
@click.option("--login", required=True)
@click.password_option()
@click.pass_obj
def login(obj, login, password):
    db = obj['db']
    user = users_service.login(db, login, password)
    obj['user'] = user


@login.command('remove_user', help="Remove user from database")
@click.option("--username", required=True)
@click.pass_obj
def remove_user(obj, username):
    db = obj['db']
    users_service.remove_user(db, username)


@login.command('create_room', help="Create new room")
@click.password_option()
@click.pass_obj
def create_room(obj, password):
    db = obj['db']
    find_room = db.find_in_db('rooms', 'owner_id', obj['user'].login)
    if find_room is None:
        rooms_service.create_room(obj['db'], obj['user'].login, password)
    elif find_room is not None:
        print("You already own a room. Delete it first, to create one.")


@login.command('delete_room', help="Delete existing room from database")
@click.option("--room_id", required=True, help="Id of room you want to delete")
@click.pass_obj
def delete_room(obj, room_id):
    db = obj['db']
    user = obj['user']
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
    for user in users_service.get_all_users(obj['db']):
        if filter is None:
            print(user.login)
        elif user.login.find(filter) > -1:
            print(user.login)


@login.command('list_rooms', help="Shows all existing rooms in database")
@click.option('--filter', help="Shows all rooms to which the given user belongs")
@click.pass_obj
def list_rooms(obj, filter=None):
    db = obj['db']
    for room in rooms_service.get_all_rooms(db):
        user_list = []
        room_owner = db.find_in_db('users', 'user_id', room.owner)
        for username in room.joined_users:
            user_name = db.find_in_db('users', 'user_id', username)
            user_list.append(user_name[1])
        if filter is None:
            print(room.id, room.topic, room.topic_desc, sorted(user_list), room_owner[1])
        elif filter in user_list:
            print(room.id, room.topic, room.topic_desc, sorted(user_list), room_owner[1])


@login.command('join_room', help="Join to existing room")
@click.option('--room_id', help="Id of room you want to join")
@click.password_option()
@click.pass_obj
def join_room(obj, room_id, password):
    db = obj['db']
    user = obj['user']
    if not rooms_service.join_room(db, user.user_id, room_id, password):
        print("Wrong room id or password!")


@login.command('change_topic', help="Change topic of room")
@click.option('--room_id', help="Id of room you want to change topic of")
@click.option('--topic', required=False, help="Name of topic you want to set")
@click.option('--desc', required=False, help="Description of topic you want to set")
@click.pass_obj
def change_topic(obj, room_id, topic, desc):
    db = obj['db']
    user = obj['user']
    if not rooms_service.update_room(db, user.user_id, room_id, topic, desc):
        print("Room doesn't exist or you are not the owner")


@login.command('remove_topic', help="Remove topic of room")
@click.option('--room_id', help="Id of room you want to remove topic of")
@click.pass_obj
def remove_topic(obj, room_id):
    db = obj['db']
    user = obj['user']
    if not rooms_service.update_room(db, user.user_id, room_id, 'None', 'None'):
        print("Room doesn't exist or you are not the owner")


@login.command('rate_topic', help="Rate existing topic of the room")
@click.option('--room_id', help="Id of room you want to rate")
@click.option('--rate', help="Integer of how do you rate topic of the room (allowed ratings: 0, 0.5, 1, 2, 3, 5, 8, "
                             "13, 20, 50, 100, 200, -1, -2")
@click.pass_obj
def rate_topic(obj, room_id, rate):
    db = obj['db']
    user = obj['user']
    if not rooms_service.update_rating_of_room(db, user.user_id, room_id, rate):
        print("You are not in the room or entered not allowed characters")


@run_application.command('register', help="Register new user")
@click.password_option()
@click.pass_obj
def register_user(obj, password):
    db = obj['db']
    login = input("Login:")
    if not users_service.validate_login(login):
        print("Wrong login!")
        return
    if not users_service.validate_password(password):
        print("Wrong password!")
        return

    if users_service.has_user(db, login):
        print("User exists!")
        return

    users_service.create_user(db, login, password)


def get_database():
    db = database.get_db(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__name__)
            ), 'database.db')
    )
    return db


if __name__ == '__main__':
    run_application()
