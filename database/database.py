import sqlalchemy as database
from sqlalchemy import MetaData
import contextlib

def clear_db(db):
    meta = MetaData()

    with contextlib.closing(db.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()

def initialize_db(db):
    db.isolation_level = None
    clear_db(db)

    db.isolation_level = ''
    db.execute('''
                    CREATE TABLE users (
                        user_id integer PRIMARY KEY,
                        login text NOT NULL UNIQUE,
                        password text NOT NULL
                    )
                ''')
    db.execute('''
                    CREATE TABLE rooms (
                        room_id integer PRIMARY KEY,
                        name text NOT NULL,
                        password text NOT NULL,
                        owner_id integer NOT NULL,
                        topic_id integer,
                        FOREIGN KEY (owner_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                ''')
    db.execute('''
                    CREATE TABLE topics (
                        topic_id integer PRIMARY KEY,
                        room_id integer NOT NULL UNIQUE,
                        topic text,
                        topic_dsc text,
                        FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
                    )
                ''')
    db.execute('''
                    CREATE TABLE user_room (
                        user_room_id integer PRIMARY KEY,
                        user_id integer NOT NULL,
                        room_id integer NOT NULL,
                        topic_rating real,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                        FOREIGN KEY (room_id) REFERENCES rooms (room_id) ON DELETE CASCADE,
                        UNIQUE(room_id, user_id)
                    )
                ''')


def get_db(path):
    engine = database.create_engine('sqlite:///'+path)
    connection = engine.connect()
    connection.execute("PRAGMA foreign_keys = ON")

    return engine
