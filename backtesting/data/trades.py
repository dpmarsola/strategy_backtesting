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

def select_trades_data_by_simulation_id(simulation_id):

    trades = []
               
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.TRADES_TABLE} WHERE simulation_id = :simulation_id', {"simulation_id" : simulation_id})
            conn.commit()
            rows = result.fetchall()
            columns = [desc[0] for desc in cursor.description]

            for row in rows:
                trade = dict(zip(columns, row))
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
        
def select_trades_sum_profit_amount(simulation_id, position_type):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT sum(profit_amount) as sum_profit FROM {constants.TRADES_TABLE} WHERE simulation_id = :simulation_id AND position_type = :position_type AND profit_amount >= 0;', {"simulation_id" : simulation_id, "position_type" : position_type})
            conn.commit()
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, result.fetchone()))
            amount = data['sum_profit']
            if  amount == None:
                return 0
            else:
                return amount
    except Exception as e:
        print(e)
        
def select_trades_sum_loss_amount(simulation_id, position_type):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT sum(profit_amount) as sum_profit FROM {constants.TRADES_TABLE} WHERE simulation_id = :simulation_id AND position_type = :position_type AND profit_amount < 0;', {"simulation_id" : simulation_id, "position_type" : position_type})
            conn.commit()
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, result.fetchone()))
            amount = data['sum_profit']
            if  amount == None:
                return 0
            else:
                return amount
    except Exception as e:
        print(e)
        
def select_trades_open_by_simulation_id(simulation_id):
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.TRADES_TABLE} WHERE simulation_id = :simulation_id AND trade_close_date = 0;', {"simulation_id" : simulation_id})
            conn.commit()
            columns = [desc[0] for desc in cursor.description]
            trade = dict(zip(columns, result.fetchone()))
            return trade
    except TypeError as te:
        return None
    except Exception as e:
        print(e)