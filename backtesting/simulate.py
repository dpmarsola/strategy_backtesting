
from . import process as ps
import pandas as pd
from . import initialize_data as init_data

start_date = '2025-08-01'
end_date = '2025-08-11'
frequency = 'D'
asset = "ITSA4"
initial_balance = 10000.00

init_data.initialize_database()

def simulate(start_date: str, end_date: str, frequency: str, asset: str, initial_balance: int, strategy: object):

    # populate the tables with initial values
    simulation_id = init_data.initialize_tables(start_date, end_date, frequency, asset, initial_balance)

    # process periods
    periods_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    for period in periods_range:
        ps.process_cycle(simulation_id, period, asset, strategy)


# simulate(start_date, end_date, frequency, asset, initial_balance, st.Strategy())