from starlette.routing import Mount

from server.api import rooms
from server.api import users

# in server/api/__init__.py
routes = [
    Mount("/users", routes=users.routes),
    Mount("/rooms", routes=rooms.routes)
]
