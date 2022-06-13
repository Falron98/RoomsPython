from starlette.routing import Route

from server.api.rooms import endpoints

routes = [
    Route('/my', endpoint=endpoints.ListRooms, methods=['GET']),
    Route('/create', endpoint=endpoints.CreateRoom, methods=['POST']),
    Route('/{id:int}', endpoint=endpoints.ShowRoom, methods=['GET']),
    Route('/{id:int}', endpoint=endpoints.UpdateRoom, methods=['PATCH']),
    Route('/{id:int}/join', endpoint=endpoints.JoinRoom, methods=['POST']),
    Route('/{id:int}/vote', endpoint=endpoints.ShowVotes, methods=['GET']),
    Route('/{id:int}/vote', endpoint=endpoints.VoteTopic, methods=['PUT']),

]
