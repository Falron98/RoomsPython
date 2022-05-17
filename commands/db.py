import os

from database import database


def clear_db(db):
    database.initialize_db(db)


def get_database():
    db = database.get_db(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__name__)
            ), 'database.sqlite')
    )
    return db
