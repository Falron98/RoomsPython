from starlette.routing import Mount

from server.api import users

# in server/api/__init__.py
routes = [
    Mount("/users", routes=users.routes),
]
