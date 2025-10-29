import sqlite3
from pathlib import Path
import backtesting.memory_store as ms

mstore = ms.MermoryStore()
class MacdSimetryInOut():
    
    description = f'''Monitors the MACD indicator and trigger a signal when there is an invertion and a confirmation on the third consecutive bar.
                                After get in, it looks for a new retraction in the MACD and trigger the get out when it reaches the same level or lower'''
    
    status_macd = None
    yesterdays_updown_macd = None
    previous_updown_macd = None
    counter_for_confirmation = 0
    yesterdays_macd = 0
    previous_macd = 0
    
    get_in_macd = 0
        
    def signal_in(self, period):
        
        self.asset = mstore.get('asset')
        self.allow_short_trades = mstore.get('allow-short')
        decision = None
        position_type = None
        
        _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,self.yesterdays_macd,cbl,_,_ = self.select_market_data_by_current_date(self.asset, period)
        
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
    
            if self.counter_for_confirmation == 2:
                self.status_macd = 'CONFIRMED'
            
        
        if self.status_macd == 'CONFIRMED':
            decision = "get_in"
            self.get_in_macd = self.yesterdays_macd

            if self.yesterdays_updown_macd == 'UP':
                position_type = 'long'
            else:
                position_type = 'short'

            if position_type == 'short' and not eval(self.allow_short_trades):
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
        
        _,_,_,high,low,_,_,_,_,adr,_,_,_,_,_,_,_,_,_,_,_,_,_,self.yesterdays_macd,cbl,_,_ = self.select_market_data_by_current_date(self.asset, period)
            
        if self.yesterdays_macd <= 0:
            self.yesterdays_updown_macd = 'DOWN'
        else:
            self.yesterdays_updown_macd = 'UP'
            
        if self.status_macd == 'WAITING_SIGNAL_OUT':

            if self.previous_updown_macd != self.yesterdays_updown_macd:
                self.status_macd = 'SIGNAL_OUT_CONFIRMED'
            
            if self.yesterdays_updown_macd == 'UP':

                if self.yesterdays_macd < (self.get_in_macd * 0.7):
                    self.status_macd = 'SIGNAL_OUT_CONFIRMED'
            
            if self.yesterdays_updown_macd == 'DOWN':

                if self.yesterdays_macd > (self.get_in_macd * 0.7):
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
                result = cursor.execute(f'SELECT *,MAX(datetime) FROM market_data WHERE asset = :asset and datetime < :datetime', {"asset" : asset, "datetime" : datetime_obj})
                conn.commit()
                ret = result.fetchone()
                return ret
        except Exception as e:
            print(e)
