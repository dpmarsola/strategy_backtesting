import sqlite3
from .. import constants


def get_connection():

    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            return conn
    except Exception as e:
        print(e)