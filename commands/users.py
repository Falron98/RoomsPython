from users import users_service


def login(db, login, password):
    return set_user_login(db, login, password)


def set_user_login(db, user_login, password):
    with db.connect() as conn:
        user = users_service.login(conn, user_login, password)
        if user is None:
            print("Wrong credentials!")
            return 'err_wrong_credentials'
    return user


def register_user(db, user_login, password):
    with db.connect() as conn:
        if not users_service.validate_login(user_login):
            print("Wrong login!")
            return 'err_wrong_data'
        if not users_service.validate_password(password):
            print("Wrong password!")
            return 'err_wrong_data'
        if users_service.has_user(conn, user_login):
            print("User exists!")
            return 'err_user_exists'

        users_service.create_user(conn, user_login, password)


def remove_user(db, user):
    with db.connect() as conn:
        users_service.remove_user(conn, user)


def list_users(db, filter=None):
    with db.connect() as conn:
        users_list = []
        for user in users_service.get_all_users(conn):
            if filter is None:
                users_list.append([user.user_id, user.login])
            elif user.login.find(filter) > -1:
                users_list.append([user.user_id, user.login])
        return users_list
