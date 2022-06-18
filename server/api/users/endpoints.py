from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from commands import users
from database.database import get_database
from starlette_jwt.middleware import createToken


class ListUsers(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request):
        user_list = []
        async with get_database() as session:
            async with session.begin():
                user = await users.list_users(session)
        for name in user:
            user_list.append({"username": name[1]})
        return JSONResponse(content=user_list)


class Register(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            data = await request.json()
        except ValueError:
            return JSONResponse({"error": "wrong_data"}, status_code=400)
        user_login = data['login']
        password = data['password']
        async with get_database() as session:
            async with session.begin():
                user_data = await users.register_user(session, user_login, password)
        if user_data == 'err_wrong_data':
            return JSONResponse({"error": "wrong_data"}, status_code=400)
        elif user_data == 'err_user_exists':
            return JSONResponse({"error": "existing_user"}, status_code=400)
        else:
            return JSONResponse({}, status_code=200)


class Login(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            data = await request.json()
        except ValueError:
            return JSONResponse({"error": "wrong_data"}, status_code=400)
        user_login = data['login']
        password = data['password']
        async with get_database() as session:
            async with session.begin():
                user_data = await users.login(session, user_login, password)
        if user_data is None or user_data == 'err_wrong_credentials':
            return JSONResponse({}, status_code=401)
        else:
            token = createToken(user_data.user_id, user_data.login)

            return JSONResponse({'token': token}, status_code=200)


class Refresh(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request):
        token = createToken(request.user.sub, request.user.username)

        return JSONResponse({'token': token}, status_code=200)
