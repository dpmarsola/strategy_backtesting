
import pandas as pd
from . import initialize_data as init_data
from . import decision_helper as dh
from . import operate as op
from . import process_cycle as pc

dhelper = dh.Decision_Helper()
operate = op.Operate()

init_data.initialize_database()

def simulate(start_date: str, end_date: str, frequency: str, asset: str, initial_balance: int, strategy: object):

    # populate the tables with initial values
    simulation_id = init_data.initialize_tables(start_date, end_date, frequency, asset, initial_balance)

    # process periods
    periods_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    for current_date in periods_range:
        print(f'Processing date: {current_date.strftime("%d/%m/%Y")}')
        pc.process_cycle(simulation_id, current_date, asset, strategy)
    
    print(f'Simulation completed!')