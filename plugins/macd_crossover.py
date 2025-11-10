import sqlite3
from pathlib import Path
import backtesting.globals as ms

global_vars = ms.Globals()
class MacdCrossOver():
    
    description = 'Monitors the MACD indicator and trigger a signal when there is an invertion and a confirmation.'
    
    status_macd = None
    yesterdays_updown_macd = None
    previous_updown_macd = None
    counter_for_confirmation = 0
    yesterdays_macd = 0
    previous_macd = 0

    def signal_in(self, period):

        self.asset = global_vars.get('asset')
        self.allow_short_trades = global_vars.get('allow-short')
        decision = None
        position_type = None
        
        result = self.select_market_data_by_current_date(self.asset, period)
        cbl = result['cbl']
        self.yesterdays_macd = result['macd_diff']
        
        if self.yesterdays_macd <= 0:
            self.yesterdays_updown_macd = 'DOWN'
        else:
            self.yesterdays_updown_macd = 'UP'

        if self.status_macd == None:
            self.status_macd = 'WAITING_FOR_CROSSOVER'
            self.previous_updown_macd = self.yesterdays_updown_macd
            
        if self.status_macd == 'WAITING_FOR_CROSSOVER':
            if self.yesterdays_updown_macd != self.previous_updown_macd:
                self.status_macd = 'WAITING_FOR_CONFIRMATION'
                self.counter_for_confirmation = 0
        
        if self.status_macd == 'WAITING_FOR_CONFIRMATION':
            
            if self.yesterdays_updown_macd == 'UP':
                if self.previous_updown_macd == 'UP':
                    if self.yesterdays_macd >= self.previous_macd:
                        self.counter_for_confirmation += 1
                    else:
                        self.counter_for_confirmation = 0
                else:
                    self.counter_for_confirmation = 1
            else:
                if self.previous_updown_macd == 'DOWN':
                    if self.yesterdays_macd <= self.previous_macd:
                        self.counter_for_confirmation += 1
                    else:
                        self.counter_for_confirmation = 0
                else:
                    self.counter_for_confirmation = 1
    
            if self.counter_for_confirmation == 3:
                self.status_macd = 'CONFIRMED'
            
        
        if self.status_macd == 'CONFIRMED':
            decision = "get_in"

            if self.yesterdays_updown_macd == 'UP':
                position_type = 'long'
            else:
                position_type = 'short'

            if position_type == 'short' and not self.allow_short_trades:
                decision = None
                position_type = None
                self.status_macd = None
                self.yesterdays_updown_macd = None
                self.previous_updown_macd = None
                self.counter_for_confirmation = 0
                self.yesterdays_macd = 0
                self.previous_macd = 0
            else:
                self.status_macd = 'WAITING_SIGNAL_OUT'
        
        self.previous_macd = self.yesterdays_macd
        self.previous_updown_macd = self.yesterdays_updown_macd
            
        return decision, position_type

    def signal_out(self, period):
        
        decision = None
        
        result = self.select_market_data_by_current_date(self.asset, period)
        high = result['high']
        low = result['low']
        cbl = result['cbl']
        adr = result['avg_daily_range']
        self.yesterdays_macd = result['macd_diff']

        if self.yesterdays_macd <= 0:
            self.yesterdays_updown_macd = 'DOWN'
        else:
            self.yesterdays_updown_macd = 'UP'
            
        if self.status_macd == 'WAITING_SIGNAL_OUT':

            if self.previous_updown_macd != self.yesterdays_updown_macd:
                self.status_macd = 'SIGNAL_OUT_CONFIRMED'
            
            if self.yesterdays_updown_macd == 'UP':

                if self.yesterdays_macd < self.previous_macd:
                    self.status_macd = 'SIGNAL_OUT_CONFIRMED'
                else:
                    if high >= adr:
                        self.status_macd = 'SIGNAL_OUT_CONFIRMED'
            
            if self.yesterdays_updown_macd == 'DOWN':

                if self.yesterdays_macd > self.previous_macd:
                    self.status_macd = 'SIGNAL_OUT_CONFIRMED'
                else:
                    if low > cbl:
                        self.status_macd = 'SIGNAL_OUT_CONFIRMED'
            
            if self.status_macd == 'SIGNAL_OUT_CONFIRMED':
                self.status_macd = None
                self.yesterdays_updown_macd = None
                self.previous_updown_macd = None
                self.counter_for_confirmation = 0
                self.yesterdays_macd = 0
                self.previous_macd = 0
                decision = 'get_out'
        
        self.previous_macd = self.yesterdays_macd
        self.previous_updown_macd = self.yesterdays_updown_macd
            
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
