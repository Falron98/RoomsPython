import datetime

import jwt
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from commands import db
from commands import users

db = db.get_database()
key = 'secret'


class ListUsers(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request):
        user_list = []
        user = users.list_users(db)
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
        user_data = users.register_user(db, user_login, password)
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
        user_data = users.login(db, user_login, password)
        if user_data == 'err_wrong_credentials':
            return JSONResponse({}, status_code=401)
        else:
            payload = {"sub": user_data.user_id,
                       "username": user_data.login,
                       "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=15)}
            token = jwt.encode(payload=payload,
                               key=key, algorithm='HS256')
            return JSONResponse({'token': token}, status_code=200)


class Refresh(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request):
        payload = {"sub": request.user.sub,
                   "username": request.user.username,
                   "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=15)}
        token = jwt.encode(payload=payload,
                           key=key, algorithm='HS256')
        return JSONResponse({'token': token}, status_code=200)
