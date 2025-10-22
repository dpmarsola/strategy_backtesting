
import pandas as pd
from . import initialize_data
from . import process_cycle 
from . import report
from . import memory_store
from . import constants
from . import parms
from .data import trades

initialize_data.database_init()
mstore = memory_store.MermoryStore()

def simulate(start_date: str, end_date: str, frequency: str, asset: str, initial_balance: int, **kwargs):

    handle_kwargs(kwargs)    

    # populate the tables with initial values
    simulation_id = initialize_data.tables_init(start_date, end_date, frequency, asset, initial_balance)
    error_message = None

    # process periods
    periods_range = pd.date_range(start=start_date, end=end_date, freq=frequency)
    
    for current_date in periods_range:
        try:
            process_result = process_cycle.execute(simulation_id, current_date, asset, force_close=False)
        except ValueError as ve:
            error_message = ve
            break

    if not error_message:
        check_for_close_on_last_day(simulation_id, asset, periods_range)
        
    report.totalizations(simulation_id, periods_range, error_message)
    
    print(f'Simulation completed!')
    
def register_strategy(strategy: object):
    
    if "type" in repr(type(strategy)):
        strategy_obj = strategy()
    else:
        strategy_obj = strategy

    if ("signal_in" not in dir(strategy_obj)) or ("signal_out" not in dir(strategy_obj)):
        raise Exception(f"Strategy does not implement the necessary methods: 'signal_in()' and 'signal_out()'.")
    
    mstore.save("strategy", strategy_obj)

def handle_kwargs(kwargs):
    
    try:
        if kwargs[constants.EXPOSABLE_PERCENTAGE]:
            mstore.save(constants.EXPOSABLE_PERCENTAGE, kwargs[constants.EXPOSABLE_PERCENTAGE])
    except KeyError as ke:
            mstore.save(constants.EXPOSABLE_PERCENTAGE, parms.DEFAULT_EXPOSABLE_PERCENTAGE)
        
    try:
        if kwargs[constants.LOT_SIZE]:
            mstore.save(constants.LOT_SIZE, kwargs[constants.LOT_SIZE])
    except KeyError as ke:
            mstore.save(constants.LOT_SIZE, parms.DEFAULT_LOT_SIZE)
        
    try:
        if kwargs[constants.PRICES_BASED_ON]:
            mstore.save(constants.PRICES_BASED_ON, kwargs[constants.PRICES_BASED_ON])
    except KeyError as ke:
            mstore.save(constants.PRICES_BASED_ON, parms.DEFAULT_PRICES_BASED_ON)
        
    try:
        if kwargs[constants.CLOSE_ON_LAST_DAY]:
            mstore.save(constants.CLOSE_ON_LAST_DAY, kwargs[constants.CLOSE_ON_LAST_DAY])
    except KeyError as ke:
            mstore.save(constants.CLOSE_ON_LAST_DAY, parms.DEFAULT_CLOSE_ON_LAST_DAY)
            
def check_for_close_on_last_day(simulation_id, asset, periods_range):
    
        # If this is true, we have an open trade    
        if mstore.get(constants.CLOSE_ON_LAST_DAY):
            for period in reversed(periods_range):
                result = process_cycle.execute(simulation_id, period, asset, force_close=True)
                if result == 0:
                    break
                
        
        # # if we got this, it means the last day was a non trading day, so we might have an open    
        # if process_result == 1:
