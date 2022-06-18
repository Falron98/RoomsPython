from sqlalchemy import Column, Integer, Text, ForeignKey, Float

from database.database import Base


class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    login = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)

    __mapper_args__ = {"eager_defaults": True}


class RoomDB(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    owner_id = Column(ForeignKey("users.user_id"), nullable=False)
    topic_id = Column(Integer)

    __mapper_args__ = {"eager_defaults": True}


class UserRoomDB(Base):
    __tablename__ = "user_room"
    user_room_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    room_id = Column(ForeignKey("rooms.room_id"), nullable=False)
    rating = Column(Float)

    __mapper_args__ = {"eager_defaults": True}


class TopicDB(Base):
    __tablename__ = "topics"
    topic_id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.room_id"), nullable=False, unique=True)
    topic = Column(Text)
    topic_dsc = Column(Text)

    __mapper_args__ = {"eager_defaults": True}
