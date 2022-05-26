class Room:
    def __init__(self, id, name, owner, password):
        self.id = id
        self.name = name
        self.owner = owner
        self.password = password


class Topic:
    def __init__(self, id: int, room_id: int, topic: str, topic_dsc: str):
        self.id = id
        self.room_id = room_id
        self.topic = topic
        self.topic_dsc = topic_dsc
