from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from commands import rooms
from database.database import get_database


class ListRooms(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request):
        logged_user = request.user.username
        rooms_list = []
        async with get_database() as session:
            async with session.begin():
                my_rooms = await rooms.list_rooms(session, logged_user)
        for one_room in my_rooms:
            rooms_list.append({"name": one_room[1], "id": one_room[0], "owner": one_room[5]})
        return JSONResponse(content=rooms_list, status_code=200)


class CreateRoom(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request):
        data = await request.json()
        name = data["name"]
        password = data['password']
        async with get_database() as session:
            async with session.begin():
                await rooms.create_room(session, request.user.sub, name, password)
        return JSONResponse({}, status_code=200)


class JoinRoom(HTTPEndpoint):
    @requires("authenticated")
    async def post(self, request: Request):
        data = await request.json()
        room_id = request.path_params['id']
        password = data['password']
        async with get_database() as session:
            async with session.begin():
                joined = await rooms.join_room(session, request.user.sub, room_id, password)
        if joined == 'err_1':
            return JSONResponse({"err": "Wrong room/password or you are already in this room"}, status_code=400)
        else:
            return JSONResponse({}, status_code=200)


class UpdateRoom(HTTPEndpoint):
    @requires("authenticated")
    async def patch(self, request: Request):
        data = await request.json()
        user_id = request.user.sub
        room_id = request.path_params['id']
        if 'topic' in data:
            topic = data['topic']
            async with get_database() as session:
                async with session.begin():
                    await rooms.change_topic(session, request.user.sub, room_id, topic, None)
        if 'password' in data:
            password = data['password']
            async with get_database() as session:
                async with session.begin():
                    await rooms.change_pass(session, request.user.sub, room_id, password)
        async with get_database() as session:
            async with session.begin():
                room = await rooms.show_room(session, user_id, room_id)
        users_dict = []
        for user in room[0][4]:
            users_dict.append({"username": user})
        return JSONResponse(content={"name": room[0][1], "id": room[0][0], "topic": room[0][2], "users": users_dict},
                            status_code=200)


class ShowVotes(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request):
        room_id = request.path_params['id']
        async with get_database() as session:
            async with session.begin():
                room_rating = await rooms.rating_of_room(session, room_id)
        votes = []
        for user in room_rating:
            votes.append({"username": user[0], "value": user[1]})
        return JSONResponse(content={"votes": votes},
                            status_code=200)


class VoteTopic(HTTPEndpoint):
    @requires("authenticated")
    async def put(self, request: Request):
        data = await request.json()
        vote = data["vote"]
        room_id = request.path_params['id']
        user_id = request.user.sub
        async with get_database() as session:
            async with session.begin():
                await rooms.rate_topic(session, user_id, room_id, vote)
        return JSONResponse(content={},
                            status_code=200)


class ShowRoom(HTTPEndpoint):
    @requires("authenticated")
    async def get(self, request: Request):
        room_id = request.path_params['id']
        user_id = request.user.sub
        async with get_database() as session:
            async with session.begin():
                room = await rooms.show_room(session, user_id, room_id)
        users_dict = []
        for user in room[0][4]:
            users_dict.append({"username": user})
        return JSONResponse(content={"name": room[0][1], "id": room[0][0], "topic": room[0][2], "users": users_dict},
                            status_code=200)
