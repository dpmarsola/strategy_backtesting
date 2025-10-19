import sqlite3
from .. import constants
import pandas as pd

def insert_trades_data(trade_open_date: str, simulation_id: str, asset_under_simulation: str, position_type: str, position_amount: int, position_quantity: int, trade_close_date: str, trade_close_amount: int, profit_amount: int, profit_percentage: int):
    
    if isinstance(trade_open_date, pd._libs.tslibs.timestamps.Timestamp):
        trade_open_date = trade_open_date.strftime("%d-%m-%Y %H:%M:%S")
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'INSERT INTO {constants.TRADES_TABLE} VALUES (:trade_open_date, :simulation_id, :asset_under_simulation, :position_type, :position_amount, :position_quantity, :trade_close_date, :trade_close_amount, :profit_amount, :profit_percentage)', 
                                    {"trade_open_date" : trade_open_date,
                                     "simulation_id" : simulation_id,
                                     "asset_under_simulation" : asset_under_simulation,
                                     "position_type" : position_type,
                                     "position_amount" : position_amount,
                                     "position_quantity" : position_quantity,
                                     "trade_close_date" : trade_close_date, 
                                     "trade_close_amount" : trade_close_amount, 
                                     "profit_amount" : profit_amount, 
                                     "profit_percentage" : profit_percentage,
                                     "simulation_id" : simulation_id}
                                    )
            conn.commit()
            return result
    except Exception as e:
        print(e)

def select_trades_data_by_simulation_id(id):

    trades = []
    
    trade = {
        "trade_open_date" : 0,
        "simulation_id" : '',
        "asset_under_simulation" : '',
        "position_type" : '',
        "position_amount" : 0,
        "position_quantity" : 0,
        "trade_close_date" : '',
        "trade_close_amount" : 0,
        "profit_amount" : 0,
        "profit_percentage" : 0,
        "positioned" : False
        }
            
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.TRADES_TABLE} WHERE simulation_id = :simulation_id', {"simulation_id" : id})
            conn.commit()
            rows = result.fetchall()
            
            for row in rows:
                
                trade['trade_open_date'] = row[0]
                trade['simulation_id'] = row[1]
                trade['asset_under_simulation'] = row[2]
                trade['position_type'] = row[3]
                trade['position_amount'] = row[4]
                trade['position_quantity'] = row[5]
                trade['trade_close_date'] = row[6]
                trade['trade_close_amount'] = row[7]
                trade['profit_percentage'] = row[8]
                
                trades.append(trade)
            
            return trades
    except Exception as e:
        print(e)
    
def update_account_position_balance(simulation_id: str, trade_open_date: str, trade_close_date: str, trade_close_amount: int, profit_amount: int, profit_percentage: int):
    
    if isinstance(trade_close_date, pd._libs.tslibs.timestamps.Timestamp):
        trade_close_date = trade_close_date.strftime("%d-%m-%Y %H:%M:%S")
        
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'UPDATE {constants.TRADES_TABLE} SET trade_close_date = :trade_close_date, trade_close_amount = :trade_close_amount, profit_amount = :profit_amount,  profit_percentage = :profit_percentage WHERE simulation_id = :simulation_id AND trade_open_date = :trade_open_date', 
                                    {"trade_close_date" : trade_close_date, 
                                     "trade_close_amount" : trade_close_amount, 
                                     "profit_amount" : profit_amount, 
                                     "profit_percentage" : profit_percentage,
                                     "simulation_id" : simulation_id,
                                     "trade_open_date" : trade_open_date}
                                    )
            conn.commit()
            return 0
    except Exception as e:
        print(e)