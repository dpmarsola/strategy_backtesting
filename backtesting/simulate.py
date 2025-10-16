
import pandas as pd
from . import initialize_data as init_data
from . import decision_helper as dh
from . import operate as op
from . import constants

dhelper = dh.Decision_Helper()
operate = op.Operate()

init_data.initialize_database()

def simulate(start_date: str, end_date: str, frequency: str, asset: str, initial_balance: int, strategy: object):

    # populate the tables with initial values
    simulation_id = init_data.initialize_tables(start_date, end_date, frequency, asset, initial_balance)

    # process periods
    periods_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    for period in periods_range:
        
        print(f'Processing date: {period.strftime("%d/%m/%Y")}')
        
        status = dhelper.check_status_positioned(simulation_id)
        
        if status["positioned"] == True:
            decision = strategy.signal_out(period)
            if decision == constants.GET_OUT:
                operate.close_position(simulation_id, period, asset)
        else:
            decision, position_type = strategy.signal_in(period)
            if decision == constants.GET_IN:
                operate.open_position(simulation_id, period, asset, position_type)
    
    print(f'Simulation completed!')