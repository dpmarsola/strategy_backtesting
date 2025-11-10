
import pandas as pd
from . import initialize_data
from . import process_cycle 
from . import report
from . import globals
from . import constants
from . import parms

initialize_data.database_init()
global_vars = globals.Globals()

def simulate(start_datetime: str, end_datetime: str, frequency: str, asset: str, initial_balance: int, **kwargs):

    # Handle keywords arguments from input
    handle_kwargs(kwargs)    

    # populate the tables with initial values
    simulation_id = initialize_data.tables_init(start_datetime, end_datetime, frequency, asset, initial_balance)

    # Store global values for later use
    global_vars.save('asset', asset)
    global_vars.save('simulation_id', simulation_id)
    global_vars.save('start_datetime', start_datetime)
    global_vars.save('end_datetime', end_datetime)
    global_vars.save('frequency', frequency)
    
    # process period
    error_message, period = process_period(simulation_id, asset, start_datetime, end_datetime, frequency)

    # Check if there is need to close on last day
    if not error_message:
        check_for_close_on_last_day(simulation_id, asset, period)

    # Generate final report
    generate_report(simulation_id, period, error_message)


# Self Functions 
def process_period(simulation_id, asset, start_datetime, end_datetime, frequency):
    
    period = pd.date_range(start=start_datetime, end=end_datetime, freq=constants.FREQUENCY_PANDAS[frequency])
    error_message = None
    
    for current_date in period:
        try:
            process_cycle.execute(simulation_id, current_date, asset, force_close=False)
        except ValueError as ve:
            error_message = ve
            break
    
    return error_message, period
    
def generate_report(simulation_id, period, error_message):
    
    final_report = report.Report(simulation_id, period, error_message)
    
    if global_vars.get(constants.OUTPUT_FILE):
        final_report.send_to_csv()
    else:
        final_report.send_to_stdout()
        final_report.plot_chart()
        
def register_strategy(strategy: object, strategy_parms: list):

    if strategy_parms:
        for parm in strategy_parms:
            if '=' not in parm:
                raise ValueError(f'Invalid strategy parm. Should contain a "key=value" pattern. See help for more information.')        
            parm = parm.split("=")
            key = parm[0]
            value = parm[1]
            global_vars.save(key, value)
            
    if "type" in repr(type(strategy)):
        strategy_obj = strategy()
    else:
        strategy_obj = strategy

    if ("signal_in" not in dir(strategy_obj)) or ("signal_out" not in dir(strategy_obj)):
        raise ValueError(f"Strategy does not implement the necessary methods: 'signal_in()' and 'signal_out()'.")
    
    global_vars.save("strategy", strategy_obj)

def handle_kwargs(kwargs):
    
    try:
        if kwargs[constants.EXPOSABLE_PERCENTAGE]:
            global_vars.save(constants.EXPOSABLE_PERCENTAGE, kwargs[constants.EXPOSABLE_PERCENTAGE])
    except KeyError as ke:
            global_vars.save(constants.EXPOSABLE_PERCENTAGE, parms.DEFAULT_EXPOSABLE_PERCENTAGE)
        
    try:
        if kwargs[constants.LOT_SIZE]:
            global_vars.save(constants.LOT_SIZE, kwargs[constants.LOT_SIZE])
    except KeyError as ke:
            global_vars.save(constants.LOT_SIZE, parms.DEFAULT_LOT_SIZE)
        
    try:
        if kwargs[constants.PRICES_BASED_ON]:
            global_vars.save(constants.PRICES_BASED_ON, kwargs[constants.PRICES_BASED_ON])
    except KeyError as ke:
            global_vars.save(constants.PRICES_BASED_ON, parms.DEFAULT_PRICES_BASED_ON)
        
    try:
        if kwargs[constants.CLOSE_ON_LAST_DAY]:
            global_vars.save(constants.CLOSE_ON_LAST_DAY, kwargs[constants.CLOSE_ON_LAST_DAY])
    except KeyError as ke:
            global_vars.save(constants.CLOSE_ON_LAST_DAY, parms.DEFAULT_CLOSE_ON_LAST_DAY)
            
    try:
        if kwargs[constants.OUTPUT_FILE]:
            global_vars.save(constants.OUTPUT_FILE, kwargs[constants.OUTPUT_FILE])
    except KeyError as ke:
            pass
            
def check_for_close_on_last_day(simulation_id, asset, period):
    
    # If this is true, we have an open trade    
    if global_vars.get(constants.CLOSE_ON_LAST_DAY):
        for date in reversed(period):
            result = process_cycle.execute(simulation_id, date, asset, force_close=True)
            if result == 0:
                break

