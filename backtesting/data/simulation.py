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

def select_simulation_data_by_id(simulation_id):
    
    simulation = { 
                    'simulation_id' : '',
                    'cycle_start' : '',
                    'cycle_end' : '',
                    'frequency' : '',
                    'asset_under_simulation' : '',
                    'initial_balance' : 0,
                    'current_balance' : 0 
                }
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.SIMULATION_TABLE} WHERE simulation_id = :simulation_id', {"simulation_id" : simulation_id})
            conn.commit()
            row = result.fetchone()
            
            if row == None:
                simulation = None
            else:
                simulation['simulation_id'] = row[0]
                simulation['cycle_start'] = row[1]
                simulation['cycle_end'] = row[2]
                simulation['frequency'] = row[3]
                simulation['asset_under_simulation'] = row[4]
                simulation['initial_balance'] = row[5]
                simulation['current_balance'] = row[6]       
            
            return simulation
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
