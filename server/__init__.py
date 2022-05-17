import uvicorn
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Mount
from starlette_jwt import JWTAuthenticationBackend

from server import api


def run():
    routes = [
        Mount("/api", routes=api.routes, name="api"),
    ]
    app = Starlette(debug=True, routes=routes)
    app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key='secret', prefix='JWT'))
    uvicorn.run(app, host="127.0.0.1", port=8000)
