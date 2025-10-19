
import pandas as pd
from . import decision_helper as dh
from . import operate as op
from . import constants

dhelper = dh.Decision_Helper()
operate = op.Operate()

def process_cycle(simulation_id, current_date, asset, strategy):
    
        trade = dhelper.check_trade_status(simulation_id)
        
        if trade["positioned"] == True:
            decision = strategy.signal_out(current_date)
            if decision == constants.GET_OUT:
                operate.close_position(simulation_id, current_date, trade, asset)
        else:
            decision, position_type = strategy.signal_in(current_date)
            if decision == constants.GET_IN:
                operate.open_position(simulation_id, current_date, asset, position_type)