from starlette.routing import Mount

from server.api import rooms
from server.api import users

routes = [
    Mount("/users", routes=users.routes),
    Mount("/rooms", routes=rooms.routes)
]
