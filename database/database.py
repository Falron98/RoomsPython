import sqlite3


def initialize_db(db: sqlite3.Connection):
    db.isolation_level = None
    for call in ["PRAGMA writable_schema = 1;",
                 "DELETE FROM sqlite_master;",
                 "PRAGMA writable_schema = 0;",
                 "VACUUM;",
                 "PRAGMA integrity_check;"]:
        db.execute(call)

    db.isolation_level = ''
    cur = db.cursor()
    cur.execute('''
                    CREATE TABLE users (
                        user_id integer PRIMARY KEY,
                        login text NOT NULL UNIQUE,
                        password text NOT NULL
                    )
                ''')
    cur.execute('''
                    CREATE TABLE rooms (
                        room_id integer PRIMARY KEY,
                        password text NOT NULL,
                        owner_id integer NOT NULL,
                        topic_id integer,
                        FOREIGN KEY (owner_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                ''')
    cur.execute('''
                    CREATE TABLE topics (
                        topic_id integer PRIMARY KEY,
                        room_id integer NOT NULL UNIQUE,
                        topic text,
                        topic_dsc text,
                        FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
                    )
                ''')
    cur.execute('''
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


def get_db(path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")

    return db
