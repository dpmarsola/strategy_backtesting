from datetime import datetime
from .data import simulation as sim
from .data import trades
from .data import initialize_db as init_db

def database_init():
    
    return init_db.create_database()
    
    
def tables_init(start_datetime, end_datetime, frequency, asset, initial_balance):

    data_dir = f'./{init_db.__package__.replace(".","/")}'
    init_db.create_tables(data_dir)
    
    # Create a new simulation ID and initilize the simulation
    curr_date = datetime.now()
    formmatted_date = curr_date.strftime("%Y%m%d_%H%M")
    simulation_id = f'sim_{formmatted_date}'
    result = sim.select_simulation_data_by_id(simulation_id)
 
    if result == None:
        sim.insert_simulation_data((simulation_id, start_datetime, end_datetime, frequency, asset, initial_balance, initial_balance))
        
    return simulation_id