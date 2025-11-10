import sys
import os
from importlib import import_module
from pathlib import Path
import argparse
import backtesting.simulate as sim

parser = argparse.ArgumentParser(prog="run_simulation.py",
                                 description="Runs a full backtesting simulation of trades based on the given parameters.")
parser.add_argument('strategy', help='Plugin Class that implements a stragey to get in ou out of a trade during simulation.')
parser.add_argument('ticker_symbol', help='The ticker symbol for the asset under simulation.')
parser.add_argument('frequency', help='The frequency for the simulation ticker analysis.')
parser.add_argument('start_datetime', help='The date the simulation will start.')
parser.add_argument('end_datetime', help='The date the simulation will end.')
parser.add_argument('initial_balance', type=int, help='The balance to begin the simulation.')
parser.add_argument('--exposable-capital', metavar='', type=int, default=100, help='Percentage of the capital the simulation can expose during a trade. DEFAULT: %(default)s (%%)')
parser.add_argument('--lot-size', metavar='', type=int, default=100, help='The number of shares in 1 lot for the market being simulated. DEFAULT: %(default)s (shares/lot)')
parser.add_argument('--prices-based-on',metavar='', default='CLOSE', help='Sets if trades will be based on the OPEN, HIGH, LOW or CLOSE value. DEFAULT:  %(default)s')
parser.add_argument('--close-on-last-day',metavar='', default=True, type=bool, help='Sets wether positions will be forced to close if the simulation ends with an open position. DEFAULT:  %(default)s')
parser.add_argument('--strategy-parms', metavar='key=value key1=value1', nargs='*', help='Pass this values as keyword parameters to the strategy class.')
parser.add_argument('--output-file', metavar='', help='When set, it will output to a file in csv format. It will override standard output.')
args = parser.parse_args()

# Add the 'plugins' directory to sys.path
plugins_directory = str(Path(__file__).parent / "plugins")
sys.path.insert(0, plugins_directory)

flag_strgy_found = False
plugin_name = ''

for item_name in os.listdir(plugins_directory):
    if args.strategy == item_name.split('.')[0]:
        flag_strgy_found = True
        break
        
if not flag_strgy_found:
    for item_name in os.listdir(plugins_directory):
        full_path = os.path.join(plugins_directory, item_name)
        if os.path.isfile(full_path):
            with open(full_path, "r") as f:
                while True:
                    line = f.readline()
                    if not line:  # Check for empty string, indicating EOF
                        break
                    if args.strategy in line.strip():
                        flag_strgy_found = True
                        args.strategy = item_name
                        args.strategy = args.strategy.replace(".py", "")
                        break
    
if flag_strgy_found:
    full_path = os.path.join(plugins_directory, item_name)
    if os.path.isfile(full_path):
        plugin_name = args.strategy

    try:
        plugin_module = import_module(plugin_name)
        for k,v in plugin_module.__dict__.items():
            if plugin_name in str(v):
                if 'class' in str(v):
                    class_name=k
        strategy = eval(f"plugin_module.{class_name}")
        start_datetime = args.start_datetime
        end_datetime = args.end_datetime
        frequency = args.frequency
        asset = args.ticker_symbol
        initial_balance = args.initial_balance
        exposable_percentage = args.exposable_capital
        lot_size = args.lot_size
        prices_based_on = args.prices_based_on
        close_on_last_day = args.close_on_last_day
        output_file = args.output_file
        strategy_parms = args.strategy_parms
        
        sim.register_strategy(strategy(), strategy_parms)
        sim.simulate(start_datetime, end_datetime, frequency, asset, initial_balance, exposable_percentage=exposable_percentage, lot_size=lot_size, prices_based_on=prices_based_on, close_on_last_day=close_on_last_day, output_file=output_file)
    except ImportError as e:
        print(f'{"-"*160}')
        print(f"Error loading plugin {plugin_name}: {e}")
        print(f'{"-"*160}')
        print(f'{" "*160}')
        print(f'{parser.print_help()}')
    except ValueError as ve:
        print(f'{"-"*160}')
        print(f'Error loading plugin {plugin_name}: {ve}')
        print(f'{"-"*160}')
        print(f'{" "*160}')
        print(f'{parser.print_help()}')

else:
    print(f'\n')
    print(f"{__file__.split('/')[-1]}: Unable to find a suitable strategy for {args.strategy}. Check the name of the plugin file.")
    print(f'\n')
    parser.print_help()
