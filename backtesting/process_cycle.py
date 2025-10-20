
import pandas as pd
from . import decision_helper as dh
from . import operate as op
from . import constants
from . import memory_store
from . import parms

dhelper = dh.Decision_Helper()
operate = op.Operate()
mstore = memory_store.MermoryStore()

def execute(simulation_id, current_date, asset):
    
    market_price = dhelper.get_asset_current_market_price(asset, current_date)
    
    if parms.PRICES_BASED_ON == constants.OPEN:
        asset_current_market_price = market_price['open']
    
    if parms.PRICES_BASED_ON == constants.HIGH:
        asset_current_market_price = market_price['high']
    
    if parms.PRICES_BASED_ON == constants.LOW:
        asset_current_market_price = market_price['low']
    
    if parms.PRICES_BASED_ON == constants.CLOSE:
        asset_current_market_price = market_price['close']
        
    if asset_current_market_price != None:
        count_trading_days()
        trade = dhelper.check_trade_status(simulation_id)
        strategy = memory_store.MermoryStore().get("strategy")
        
        if trade["positioned"] == True:
            decision = strategy.signal_out(current_date)
            if decision == constants.GET_OUT:
                operate.close_position(simulation_id, current_date, trade, asset, asset_current_market_price)
        else:
            decision, position_type = strategy.signal_in(current_date)
            if decision == constants.GET_IN:
                operate.open_position(simulation_id, current_date, asset, asset_current_market_price, position_type)
                
def count_trading_days():
    
    count_number_trading_days = mstore.get("counter_testing_days")
    
    if count_number_trading_days == None:
        mstore.save("counter_testing_days", 0)
        count_number_trading_days = 0
    
    count_number_trading_days += 1
    
    mstore.save("counter_testing_days", count_number_trading_days)