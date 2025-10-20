from .data import simulation as sim
from .data import trades as trd
from .data import market_data as mkt
from . import parms
from . import constants


class Decision_Helper():
    
    flag = True
    position_type = ""
    position_amount = 0
    position_quantity = 0

    def check_trade_status(self, simulation_id):
        
        
        try:
            trades = trd.select_trades_data_by_simulation_id(simulation_id)
            
            if len(trades) == 0:
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
            else:
                for trade in trades:
                    if trade['trade_close_amount'] == 0:
                        trade['positioned'] = True
                        break
        except Exception as e:
            trade['positioned'] = False

        return trade

    def determine_amount_to_expose(self, simulation_id):

        simulation = sim.select_simulation_data_by_id(simulation_id)
        
        exposable_amount = simulation['current_balance'] * (int(parms.EXPOSABLE_PERCENTAGE)) // 100
        
        return exposable_amount
        
    def get_asset_current_market_price(self, asset, current_date):
        
        market_price = { 
            "period" : None,
            "open" : None,
            "high" : None,
            "low" : None,
            "close" : None
        }
        
        try:
            current_market_price = mkt.select_market_data_by_current_date(asset, current_date)
            market_price['open'] = current_market_price[1]
            market_price['high'] = current_market_price[2]
            market_price['low'] = current_market_price[3]
            market_price['close'] = current_market_price[4]
        except Exception as e:
            return market_price            
            
        return market_price