import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Mount
from starlette_jwt import JWTAuthenticationBackend

from server import api


def run():
    routes = [
        Mount("/api", routes=api.routes, name="api"),
    ]
    middleware = [
        Middleware(TrustedHostMiddleware, allowed_hosts=['*']),
        Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
        Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key='secret'))
    ]
    app = Starlette(debug=True, routes=routes, middleware=middleware)
    uvicorn.run(app, host="127.0.0.1", port=8000)
