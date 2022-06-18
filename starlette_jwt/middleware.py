import datetime

import jwt
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)
from typing import Optional, Tuple, Union

key = 'secret'


def createToken(id, login):
    payload = {"sub": id,
               "username": login,
               "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=15)}
    token = jwt.encode(payload=payload,
                       key=key, algorithm='HS256')
    return token


class JWTUser(BaseUser):
    def __init__(self, sub: int, username: str, token: str, payload: dict) -> None:
        self.sub = sub
        self.username = username
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class JWTAuthenticationBackend(AuthenticationBackend):

    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 prefix: str = 'JWT',
                 username_field: str = 'username',
                 sub: str = 'sub',
                 audience: Optional[str] = None,
                 options: Optional[dict] = None) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field
        self.sub = sub
        self.audience = audience
        self.options = options or dict()

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm, audience=self.audience,
                                 options=self.options)
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), JWTUser(sub=payload[self.sub], username=payload[self.username_field],
                                                           token=token,
                                                           payload=payload)


class JWTWebSocketAuthenticationBackend(AuthenticationBackend):

    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 query_param_name: str = 'jwt',
                 sub: str = 'sub',
                 username_field: str = 'username',
                 audience: Optional[str] = None,
                 options: Optional[dict] = None) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.query_param_name = query_param_name
        self.sub = sub
        self.username_field = username_field
        self.audience = audience
        self.options = options or dict()

    async def authenticate(self, request) -> Tuple[AuthCredentials, BaseUser]:
        if self.query_param_name not in request.query_params:
            return AuthCredentials(), UnauthenticatedUser()

        token = request.query_params[self.query_param_name]

        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm, audience=self.audience,
                                 options=self.options)
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e))

        return AuthCredentials(["authenticated"]), JWTUser(sub=payload[self.sub], username=payload[self.username_field],
                                                           token=token,
                                                           payload=payload)
