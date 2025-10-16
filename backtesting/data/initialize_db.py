import sqlite3
import os
from .. import constants

def create_database():
    # Define the database file name
    database_file = constants.DATABASE_NAME

    if os.path.exists(database_file):
        return 0
    else:
        print(f"Creating Database '{database_file}'.")

    try:
        # Connect to the database. If the file doesn't exist, it will be created.
        conn = sqlite3.connect(database_file)
        print(f"Database '{database_file}' created successfully or connected to existing database.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        if 'conn' in locals() and conn:
            conn.close()
    
    return conn


def create_tables(location):   
    
    # Define the database file name
    database_file = constants.DATABASE_NAME     

    try:
        conn = sqlite3.connect(database_file)
        with open(f'{location}/create_tables.sql') as f:
            sql_statements = f.read().split(";")

        for statement in sql_statements:
            cursor = conn.cursor()
            cursor.execute(statement)
            conn.commit() # Commit the changes to the database
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        if 'conn' in locals() and conn:
            conn.close()