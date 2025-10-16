import sqlite3
from .. import constants

def insert_account_position_data(account_data):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'INSERT INTO {constants.ACCOUNT_POSITION_TABLE} VALUES (:account_id, :account_name, :position_type, :position_amount, :position_quantity, :simulation_id)', account_data)
            conn.commit()
            return result
    except Exception as e:
        print(e)

def select_account_position_data_by_id(id):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.ACCOUNT_POSITION_TABLE} WHERE account_id = :account_id', {"account_id" : id})
            conn.commit()
            return result.fetchone()
    except Exception as e:
        print(e)

def select_account_position_data_by_simulation_id(id):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.ACCOUNT_POSITION_TABLE} WHERE simulation_id = :simulation_id', {"simulation_id" : id})
            conn.commit()
            return result.fetchone()
    except Exception as e:
        print(e)
    
def update_account_position_balance(simulation_id, position_amount, position_type, position_quantity):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'UPDATE {constants.ACCOUNT_POSITION_TABLE} SET position_amount = :position_amount, position_type = :position_type, position_quantity = :position_quantity WHERE simulation_id = :simulation_id', {"position_amount" : position_amount, "simulation_id" : simulation_id, "position_type" : position_type, "position_quantity" : position_quantity})
            conn.commit()
            return 0
    except Exception as e:
        print(e)