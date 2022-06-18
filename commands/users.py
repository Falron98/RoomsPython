from sqlalchemy.ext.asyncio import AsyncSession

from users import users_service


async def login(db: AsyncSession, login, password):
    return await set_user_login(db, login, password)


async def set_user_login(db: AsyncSession, user_login, password):
    user = await users_service.login(db, user_login, password)
    if user is None:
        print("Wrong credentials!")
        return 'err_wrong_credentials'
    return user


async def register_user(db: AsyncSession, user_login, password):
    if not users_service.validate_login(user_login):
        print("Wrong login!")
        return 'err_wrong_data'
    if not users_service.validate_password(password):
        print("Wrong password!")
        return 'err_wrong_data'
    if await users_service.has_user(db, user_login):
        print("User exists!")
        return 'err_user_exists'
    return await users_service.create_user(db, user_login, password)


async def remove_user(db: AsyncSession, user):
    await users_service.remove_user(db, user)


async def list_users(db: AsyncSession, filter=None):
    users_list = []
    for user in await users_service.get_all_users(db):
        if filter is None:
            users_list.append([user.user_id, user.login])
        elif user.login.find(filter) > -1:
            users_list.append([user.user_id, user.login])
    return users_list
