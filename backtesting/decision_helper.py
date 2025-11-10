from .data import simulation as sim
from .data import trades
from .data import market_data as mkt
from . import parms
from . import globals
from . import constants

global_vars=globals.Globals()
class Decision_Helper():
    
    flag = True
    position_type = ""
    position_amount = 0
    position_quantity = 0

    def check_trade_status(self, simulation_id):
        
        
        try:
            trade = trades.select_trades_open_by_simulation_id(simulation_id)
            
            if trade == None:
                trade = {
                    "positioned" : False
                }
            else:
                if trade['trade_close_date'] == 0:
                    trade['positioned'] = True
        except Exception as e:
            trade['positioned'] = False

        return trade

    def determine_amount_to_expose(self, simulation_id):

        simulation = sim.select_simulation_data_by_id(simulation_id)
        
        exposable_amount = simulation['current_balance'] * (int(global_vars.get(constants.EXPOSABLE_PERCENTAGE))) // 100
        
        return exposable_amount
        
    def get_asset_current_market_price(self, asset, current_date):

        result =  mkt.select_market_data_by_current_date(asset, current_date)
        return result