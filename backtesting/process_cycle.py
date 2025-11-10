
import pandas as pd
from . import decision_helper as dh
from . import operate as op
from . import constants
from . import globals
from . import parms

dhelper = dh.Decision_Helper()
operate = op.Operate()
global_vars = globals.Globals()

def execute(simulation_id, current_date, asset, force_close=False):
    
    market_price = dhelper.get_asset_current_market_price(asset, current_date)
    prices_based_on = global_vars.get(constants.PRICES_BASED_ON)
    
    asset_current_market_price = None
    
    if prices_based_on.lower() == constants.OPEN.lower():
        asset_current_market_price = market_price['open']
    
    if prices_based_on.lower() == constants.HIGH.lower():
        asset_current_market_price = market_price['high']
    
    if prices_based_on.lower() == constants.LOW.lower():
        asset_current_market_price = market_price['low']
    
    if prices_based_on.lower() == constants.CLOSE.lower():
        asset_current_market_price = market_price['close']
        
    if asset_current_market_price != None:
        trade = dhelper.check_trade_status(simulation_id)
        strategy = globals.Globals().get("strategy")
        
        if trade["positioned"] == True:            
            if force_close == True:
                operate.close_position(simulation_id, current_date, trade, asset, asset_current_market_price)
                return 0
            else:
                decision = strategy.signal_out(current_date)
                if decision == constants.GET_OUT:
                    operate.close_position(simulation_id, current_date, trade, asset, asset_current_market_price)
        else:
            # If this force_close is true, it means we'are in the CLOSE_ON_LAST_DAY state. This state only needs to CLOSE a position, previously open.
            # Let's prevent from opening a position if we got here on the last day.
            if force_close == True:
                pass
            else:
                decision, position_type = strategy.signal_in(current_date)
                if decision == constants.GET_IN:
                    operate.open_position(simulation_id, current_date, asset, asset_current_market_price, position_type)
                
        count_trading_days()
        
        return 0
    else:
        return 1
                
def count_trading_days():
    
    count_number_trading_days = global_vars.get("counter_testing_days")
    
    if count_number_trading_days == None:
        global_vars.save("counter_testing_days", 0)
        count_number_trading_days = 0
    
    count_number_trading_days += 1
    
    global_vars.save("counter_testing_days", count_number_trading_days)