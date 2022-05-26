import click
import pandas as pd

import database.database
import server
from commands import db
from commands import rooms
from commands import users


@click.group()
@click.pass_context
def run_application(ctx):
    ctx.obj = {'db': db.get_database()}


@run_application.command('run_as_server', help="Runs uvicorn server")
def run_as_server():
    server.run()


@run_application.command('initialize-db', help="Recreate DB")
@click.pass_obj
def clear_db(obj):
    db = obj['db']
    database.database.initialize_db(db)


@run_application.group('login', help="Login as existing user")
@click.option("--login", required=True, help="Login of account you want to log in")
@click.password_option()
@click.pass_obj
def login(obj, login, password):
    db = obj['db']
    obj['user'] = users.login(db, login, password)


@login.command('remove_user', help="Remove user from database")
@click.option("--user", required=True)
@click.pass_obj
def remove_user(obj, user):
    db = obj['db']
    users.remove_user(db, user)


@login.command('create_room', help="Create new room")
@click.password_option()
@click.pass_obj
def create_room(obj, password):
    db = obj['db']
    user = obj['user']
    name = input("Name of room: ")
    rooms.create_room(db, user.user_id, name, password)


@login.command('delete_room', help="Delete existing room from database")
@click.option("--room_id", required=True, help="Id of room you want to delete")
@click.pass_obj
def delete_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    rooms.delete_room(db, user.user_id, room_id)


@login.command('list_users', help="Shows all existing users in database")
@click.option('--filter', help="Filters users by given characters")
@click.pass_obj
def list_users(obj, filter=None):
    db = obj['db']
    users_list = users.list_users(db, filter)
    df = pd.DataFrame(users_list, columns=['ID', 'Login'])
    print(df)


@login.command('list_rooms', help="Shows all existing rooms in database")
@click.option('--filter', help="Shows all rooms to which the given user belongs")
@click.pass_obj
def list_rooms(obj, filter=None):
    db = obj['db']
    rooms_list = rooms.list_rooms(db, filter)
    df = pd.DataFrame(rooms_list, columns=['ID', 'Topic', 'Description', 'Users in room', 'Owner'])
    print(df)


@login.command('show_room', help="Show existing room")
@click.option('--room_id', required=True, help="Id of room you want to show")
@click.pass_obj
def show_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    rooms_list = rooms.show_room(db, user.user_id, room_id)
    if rooms_list is not None:
        df = pd.DataFrame(rooms_list, columns=['ID', 'Topic', 'Description', 'Users in room', 'Owner'])
        print(df)
        users_ratings = rooms.rating_of_room(db, room_id)
        df = pd.DataFrame(users_ratings, columns=['User', 'Rating of Topic'])
        print(df)


@login.command('join_room', help="Join to existing room")
@click.option('--room_id', help="Id of room you want to join")
@click.password_option()
@click.pass_obj
def join_room(obj, room_id, password):
    db = obj['db']
    user = obj['user']
    rooms.join_room(db, user.user_id, room_id, password)


@login.command('leave_room', help="Leave room you are in")
@click.option('--room_id', help="Id of room you want to leave")
@click.pass_obj
def leave_room(obj, room_id):
    db = obj['db']
    user = obj['user']
    rooms.leave_room(db, user.user_id, room_id)


@login.command('change_topic', help="Change topic of room")
@click.option('--room_id', help="Id of room you want to change topic of")
@click.option('--topic', required=False, help="Name of topic you want to set")
@click.option('--desc', required=False, help="Description of topic you want to set")
@click.pass_obj
def change_topic(obj, room_id, topic, desc):
    db = obj['db']
    user = obj['user']
    rooms.change_topic(db, user.user_id, room_id, topic, desc)


@login.command('remove_topic', help="Remove topic of room")
@click.option('--room_id', help="Id of room you want to remove topic of")
@click.pass_obj
def remove_topic(obj, room_id):
    db = obj['db']
    user = obj['user']
    rooms.remove_topic(db, user.user_id, room_id)


@login.command('rate_topic', help="Rate existing topic of the room")
@click.option('--room_id', required=True, help="Id of room you want to rate")
@click.option('--rate', required=True, help="Integer of how do you rate topic of the room (allowed ratings: 0, 0.5, "
                                            "1, 2, 3, 5, 8, 13, 20, 50, 100, 200, -1, -2")
@click.pass_obj
def rate_topic(obj, room_id, rate):
    db = obj['db']
    user = obj['user']
    rooms.rate_topic(db, user.user_id, room_id, rate)


@run_application.command('register', help="Register new user")
@click.password_option()
@click.pass_obj
def register_user(obj, password):
    db = obj['db']
    login = input("Login: ")
    users.register_user(db, login, password)


if __name__ == '__main__':
    run_application()
