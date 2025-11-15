import sqlite3
from pathlib import Path
import backtesting.globals as ms
import backtesting.constants as constants

global_vars = ms.Globals()
class EmaCrossover():
    
    description = f'''When a Fast EMA crosses above the Slow EMA it trigger a buy signal, otherwise it triggers a sell one.'''
    
    status_crossover = None
    yesterdays_emaf4_below_above = None
    previous_emaf4_below_above = None
        
    def signal_in(self, period):
        
        self.asset = global_vars.get('asset')
        self.allow_short_trades = eval(global_vars.get('allow-short'))
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
                result = cursor.execute(f'SELECT *,MAX(datetime) FROM historical_data WHERE asset = :asset and datetime < :datetime', {"asset" : asset, "datetime" : datetime_obj})
                conn.commit()
                columns = [desc[0] for desc in cursor.description]
                market_data = dict(zip(columns, result.fetchone()))
                return market_data
        except Exception as e:
            print(e)
