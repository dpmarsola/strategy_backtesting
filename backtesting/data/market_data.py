import sqlite3
from .. import constants

def select_market_data_by_period(asset, period):
    
    datetime_obj = period.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(f'SELECT * FROM {constants.MARKET_DATA_TABLE} WHERE asset = :asset and datetime = :datetime', {"asset" : asset, "datetime" : datetime_obj})
            conn.commit()
            return result.fetchone()
    except Exception as e:
        if "no such table" in e.__str__():
            print(f'Table {constants.MARKET_DATA_TABLE} not found in database {constants.DATABASE_NAME}. Run script to fetch market data.')