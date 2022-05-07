import os
import sqlite3


class Database:
    def __init__(self, path):
        self.path = path

    def init(self):
        self._check_db_exists()

    def put_to_db(self, table_name, **values):
        con = self.open_connection()
        cur = con.cursor()
        key_list = []
        values_list = []
        for key, value in values.items():
            key_list.append(key)
            values_list.append(value)
        key_list = tuple(key_list)
        key_list = ', '.join(key_list)
        values_list = tuple(values_list)
        qst_marks = self.qst_marks(values_list)
        cur.execute("INSERT INTO " + table_name + " (" + key_list + ") VALUES(" + qst_marks + ")", values_list)
        con.commit()

    def update_to_db(self, table_name, column_name, condition_name, *values):
        con = self.open_connection()
        cur = con.cursor()
        cur.execute("UPDATE " + table_name + " SET " + column_name + " = ? WHERE " + condition_name + " = ?", values)
        con.commit()

    def update_to_db_2(self, table_name, column_name, condition_name1, condition_name2, *values):
        con = self.open_connection()
        cur = con.cursor()
        cur.execute("UPDATE " + table_name + " SET " + column_name + " = ? WHERE " + condition_name1 + " = ? AND " + condition_name2 + " = ?", values)
        con.commit()

    def qst_marks(self, keylist):
        questions = "?"
        length = 0
        while length < len(keylist)-1:
            questions += ", ?"
            length += 1
        return questions

    def remove_from_db(self, table_name, row_name, *values):
        con = self.open_connection()
        cur = con.cursor()
        values_list = ' '.join(values)
        cur.execute("DELETE FROM " + table_name + " WHERE " + row_name + " = '" + values_list + "'")
        con.commit()

    def remove_from_db2(self, table_name, condition_name1, condition_name2, *values):
        con = self.open_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM " + table_name + " WHERE " + condition_name1 + " = ? AND " + condition_name2 + " = ?", values)
        con.commit()

    def find_in_db(self, table_name, search_row, *values):
        con = self.open_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM " + table_name + " WHERE " + search_row + " = ?", values)
        record = cur.fetchone()
        if self._match(record):
            return record
        return None

    def find_all_in_db(self, table_name, *values):
        con = self.open_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM " + table_name + " " + ' '.join(values))
        record = cur.fetchall()
        if self._match(record):
            return record
        return None

    def open_connection(self):
        con = sqlite3.connect(self.path)
        return con

    def initialize_db(self):
        try:
            os.stat(self.path)
        except FileNotFoundError:
            db = self.open_connection()
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
                            FOREIGN KEY(topic_id) REFERENCES topics(topic_id)
                        )
                    ''')
            cur.execute('''
                        CREATE TABLE topics (
                            topic_id integer PRIMARY KEY,
                            topic text,
                            topic_dsc text,
                            room_id integer,
                            FOREIGN KEY(room_id) REFERENCES rooms(room_id)
                        )
                    ''')
            cur.execute('''
                        CREATE TABLE user_room (
                            user_id integer,
                            room_id integer,
                            topic_rating real,
                            CONSTRAINT user_room_pk PRIMARY KEY (user_id, room_id),
                            CONSTRAINT FK_user FOREIGN KEY (user_id) REFERENCES users (user_id),
                            CONSTRAINT FK_room FOREIGN KEY (room_id) REFERENCES rooms (room_id)
                        )
                    ''')
            db.commit()
        else:
            os.remove(self.path)
            self.initialize_db()
            return

    def _check_db_exists(self):
        try:
            os.stat(self.path)
        except FileNotFoundError:
            self.initialize_db()

    def _match(self, row, *values):
        for index, value in enumerate(values):
            if value is None or row is None:
                continue
            if row[index + 1] != value:
                return False

        return True


def get_db(path):
    db = Database(path)
    db.init()

    return db
