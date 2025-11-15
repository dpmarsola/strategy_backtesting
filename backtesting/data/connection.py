import sqlite3
import backtesting.constants as constants


def get_connection():

    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            return conn
    except Exception as e:
        print(e)