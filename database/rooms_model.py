class Room:
    def __init__(self, id, owner, password, joined_users, topic, topic_desc):
        self.id = id
        self.owner = owner
        self.password = password
        self.joined_users = joined_users
        self.topic = topic
        self.topic_desc = topic_desc