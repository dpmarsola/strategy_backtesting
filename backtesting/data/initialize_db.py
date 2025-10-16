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
        
        script_create_tables = ('DROP TABLE IF EXISTS simulation;', 

                                f'''CREATE TABLE IF NOT EXISTS simulation (
                                        simulation_id TEXT PRIMARY KEY NOT NULL,
                                        cycle_start TEXT NOT NULL,
                                        cycle_end TEXT NOT NULL,
                                        frequency TEXT NOT NULL,
                                        asset_under_simulation TEXT NOT NULL,
                                        initial_balance NUMERIC NOT NULL,
                                        current_balance NUMERIC NOT NULL
                                    );''',

                                    f'''DROP TABLE IF EXISTS account_position;''',

                                    f'''CREATE TABLE IF NOT EXISTS account_position (
                                        account_id TEXT PRIMARY KEY NOT NULL,
                                        account_name TEXT NOT NULL,
                                        position_type TEXT NOT NULL,
                                        position_amount NUMERIC NOT NULL,
                                        position_quantity NUMERIC NOT NULL,
                                        simulation_id TEXT NOT NULL,
                                        FOREIGN KEY(simulation_id) REFERENCES simulation(simulation_id)
                                    );''')

        for statement in script_create_tables:
            
            # You can now perform database operations using the 'conn' object.
            # For example, create a table:
            cursor = conn.cursor()
            cursor.execute(statement)
            conn.commit() # Commit the changes to the database

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")
        
        return database_file