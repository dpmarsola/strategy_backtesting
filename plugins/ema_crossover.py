import sqlite3
from pathlib import Path
import backtesting.memory_store as ms
import backtesting.constants as constants

mstore = ms.MermoryStore()
class EmaCrossover():
    
    description = f'''When a Fast EMA crosses above the Slow EMA it trigger a buy signal, otherwise it triggers a sell one.'''
    
    status_crossover = None
    yesterdays_emaf4_below_above = None
    previous_emaf4_below_above = None
        
    def signal_in(self, period):
        
        self.asset = mstore.get('asset')
        self.allow_short_trades = eval(mstore.get('allow-short'))
        decision = None
        position_type = None
        market_data = self.select_market_data_by_current_date(self.asset, period)
        emaf4 = market_data['ema_f4']
        emas1 = market_data['ema_s1']
        
        if emaf4 < emas1:
            self.yesterdays_emaf4_below_above = "below"
        else:
            self.yesterdays_emaf4_below_above = "above"

        if self.status_crossover == None:
            self.status_crossover = 'WAITING_FOR_CROSSOVER'
            self.previous_emaf4_below_above = self.yesterdays_emaf4_below_above
            
            
        if self.status_crossover == 'WAITING_FOR_CROSSOVER':
            if self.yesterdays_emaf4_below_above != self.previous_emaf4_below_above:
                self.status_crossover = 'CONFIRMED'
        
        if self.status_crossover == 'CONFIRMED':
            position_type = constants.LONG if self.yesterdays_emaf4_below_above == "above" else constants.SHORT
            decision = constants.GET_IN
            self.status_crossover = 'WAITING_FOR_SIGNAL_OUT'
         
        self.previous_emaf4_below_above = self.yesterdays_emaf4_below_above
        return decision, position_type

    def signal_out(self, period):
        
        decision = None
        
        market_data = self.select_market_data_by_current_date(self.asset, period)
        emaf4 = market_data['ema_f4']
        emas1 = market_data['ema_s1']
        
        if emaf4 < emas1:
            self.yesterdays_emaf4_below_above = "below"
        else:
            self.yesterdays_emaf4_below_above = "above"
            
        if self.status_crossover == 'WAITING_FOR_SIGNAL_OUT':
            if self.yesterdays_emaf4_below_above != self.previous_emaf4_below_above:
                self.status_crossover = 'SIGNAL_OUT_CONFIRMED'
        
        if self.status_crossover == 'SIGNAL_OUT_CONFIRMED':
            self.status_crossover = None
            self.yesterdays_emaf4_below_above = None
            self.previous_emaf4_below_above = None
            decision = constants.GET_OUT
        
        self.previous_emaf4_below_above = self.yesterdays_emaf4_below_above
        return decision


    def select_market_data_by_current_date(self, asset, current_date):
        
        datetime_obj = current_date.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with sqlite3.connect(f'data.db') as conn:
                cursor = conn.cursor()
                result = cursor.execute(f'SELECT *,MAX(datetime) FROM market_data WHERE asset = :asset and datetime < :datetime', {"asset" : asset, "datetime" : datetime_obj})
                conn.commit()
                row = result.fetchone()
                market_data = {
                        "datetime": row[0],
                        "time": row[1],
                        "open": row[2],
                        "high": row[3],
                        "low": row[4],
                        "close": row[5],
                        "tick_volume": row[6],
                        "spread": row[7],
                        "real_volume": row[8],
                        "avg_daily_range": row[9],
                        "ema_f1": row[10],
                        "ema_f2": row[11],
                        "ema_f3": row[12],
                        "ema_f4": row[13],
                        "ema_f5": row[14],
                        "ema_f6": row[15],
                        "ema_s1": row[16],
                        "ema_s2": row[17],
                        "ema_s3": row[18],
                        "ema_s4": row[19],
                        "ema_s5": row[20],
                        "ema_s6": row[21],
                        "avg_true_range": row[22],
                        "macd_diff": row[23],
                        "cbl": row[24],
                        "asset": row[25]
                    }
                return market_data
        except Exception as e:
            print(e)
