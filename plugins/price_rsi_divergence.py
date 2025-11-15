import sqlite3
from pathlib import Path
import backtesting.globals as ms

global_vars = ms.Globals()
class MacdCrossOver():
    
    description = 'Monitors the MACD indicator and trigger a signal when there is an invertion and a confirmation.'
    
    def signal_in(self, period):

        return decision, position_type

    def signal_out(self, period):
        
        decision = None
        

        return decision


    def select_market_data_by_current_date(self, asset, current_date):
        
        datetime_obj = current_date.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with sqlite3.connect(f'data.db') as conn:
                cursor = conn.cursor()
                result = cursor.execute(f'SELECT *,MAX(datetime) FROM historical_data WHERE asset = :asset and datetime < :datetime', {"asset" : asset, "datetime" : datetime_obj})
                conn.commit()
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, result.fetchone()))
                return data
        except Exception as e:
            print(e)
