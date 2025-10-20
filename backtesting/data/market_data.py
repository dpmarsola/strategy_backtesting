import sqlite3
from .. import constants

def select_market_data_by_current_date(asset, current_date):
    
    datetime_obj = current_date.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.MARKET_DATA_TABLE} WHERE asset = :asset and datetime = :datetime', {"asset" : asset, "datetime" : datetime_obj})
            conn.commit()
            return result.fetchone()
    except Exception as e:
        if "no such table" in e.__str__():
            print(f'Table {constants.MARKET_DATA_TABLE} not found in database {constants.DATABASE_NAME}. Run script to fetch market data.')
            
            
def select_all_market_data_by_period(asset, period_start, period_end):
    
    datetime_start_obj = period_start.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    datetime_end_obj = period_end.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    
    market_data = []
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.MARKET_DATA_TABLE} WHERE asset = :asset AND datetime BETWEEN :datetime_start AND :datetime_end', {"asset" : asset, "datetime_start" : datetime_start_obj, "datetime_end" : datetime_end_obj})
            conn.commit()
            rows = result.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            for row in rows:
                data = dict(zip(columns, row))
                market_data.append(data)
            
            return market_data
    except Exception as e:
        if "no such table" in e.__str__():
            print(f'Table {constants.MARKET_DATA_TABLE} not found in database {constants.DATABASE_NAME}. Run script to fetch market data.')