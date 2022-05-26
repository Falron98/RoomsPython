from starlette.routing import Route

from server.api.users import endpoints

routes = [
    Route('/register', endpoint=endpoints.Register, methods=['POST']),
    Route('/login', endpoint=endpoints.Login, methods=['POST']),
    Route('/refresh', endpoint=endpoints.Refresh, methods=['POST']),
    Route('/list', endpoint=endpoints.ListUsers, methods=['GET'])
]
