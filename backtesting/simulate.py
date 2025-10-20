
import pandas as pd
from . import initialize_data
from . import process_cycle 
from . import report
from . import memory_store

initialize_data.database_init()
mstore = memory_store.MermoryStore()

def simulate(start_date: str, end_date: str, frequency: str, asset: str, initial_balance: int):

    # populate the tables with initial values
    simulation_id = initialize_data.tables_init(start_date, end_date, frequency, asset, initial_balance)

    # process periods
    periods_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    for current_date in periods_range:
        print(f'Processing date: {current_date.strftime("%d/%m/%Y")}')
        process_cycle.execute(simulation_id, current_date, asset)
        
    report.totalizations(simulation_id, periods_range)
    
    print(f'Simulation completed!')
    
def register_strategy(strategy: object):
    
    if "type" in repr(type(strategy)):
        strategy_obj = strategy()
    else:
        strategy_obj = strategy

    if ("signal_in" not in dir(strategy_obj)) or ("signal_out" not in dir(strategy_obj)):
        raise Exception(f"Strategy does not implement the necessary methods: 'signal_in()' and 'signal_out()'.")
    
    mstore.save("strategy", strategy_obj)