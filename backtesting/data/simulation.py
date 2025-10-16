import sqlite3
from .. import constants


def insert_simulation_data(simulation_data):

    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'INSERT INTO {constants.SIMULATION_TABLE} VALUES (:simulation_id, :cycle_start, :cycle_end, :frequency, :asset_under_simulation, :initial_balance, :current_balance)', simulation_data)
            conn.commit()
            return result
    except Exception as e:
        print(e)

def select_simulation_data_by_id(id):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.SIMULATION_TABLE} WHERE simulation_id = :simulation', {"simulation" : id})
            conn.commit()
            return result.fetchone()
    except Exception as e:
        print(e)
    
def update_simulation_current_balance(simulation_id,amount,subtraction):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.SIMULATION_TABLE} WHERE simulation_id = :simulation_id', {"simulation_id" : simulation_id})
            conn.commit()
            _,_,_,_,_,_,current_balance = result.fetchone()
            
            if subtraction:
                current_balance = current_balance - amount
            else:
                current_balance = current_balance + amount
            
            result = cursor.execute(f'UPDATE {constants.SIMULATION_TABLE} SET current_balance = :current_balance WHERE simulation_id = :simulation_id', {"current_balance" : current_balance, "simulation_id" : simulation_id})
            conn.commit()
            return 0
    except Exception as e:
        print(e)
    