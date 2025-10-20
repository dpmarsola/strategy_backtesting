from .data import simulation
from .data import trades
from .data import market_data
from . import constants
from . import parms
from . import memory_store
import pandas as pd

mstore = memory_store.MermoryStore()

def totalizations(simulation_id: str, period: str):
    
    # getting the data need from the tables
    simulation_data = simulation.select_simulation_data_by_id(simulation_id)
    trades_data = trades.select_trades_data_by_simulation_id(simulation_id)
    
    # initializing variables for the totals 
    total_short_trades = 0
    total_long_trades = 0
    total_short_winner_trades = 0
    total_long_winner_trades = 0
    total_short_loser_trades = 0
    total_long_loser_trades = 0
    largest_short_profit_trade = 0
    largest_long_profit_trade = 0
    largest_short_loss_trade = 0
    largest_long_loss_trade = 0
    consecutive_wins = 0
    consecutive_losses = 0
    maximum_consecutive_wins = 0
    maximum_consecutive_losses = 0
    average_consecutive_wins = 0
    average_consecutive_losses = 0

    # auxiliary varibales for calculations    
    previous_result = ""
    current_result = ""
    aux = 0
    list_consecutive_wins = []
    list_consecutive_losses = []
    
    for trade in trades_data:
        aux += 1
        
        if trade['position_type'] == constants.SHORT:
            total_short_trades += 1
            if trade['profit_amount'] >= 0:
                total_short_winner_trades += 1
                current_result = constants.WIN
                consecutive_wins += 1
                if trade['profit_amount'] > largest_short_profit_trade:
                    largest_short_profit_trade = trade['profit_amount']
            else:
                total_short_loser_trades += 1
                current_result = constants.LOOSE
                consecutive_losses += 1
                if trade['profit_amount'] < largest_short_loss_trade:
                    largest_short_loss_trade = trade['profit_amount']
        
        if trade['position_type'] == constants.LONG:
            total_long_trades += 1
            if trade['profit_amount'] >= 0:
                total_long_winner_trades += 1
                current_result = constants.WIN
                consecutive_wins += 1
                if trade['profit_amount'] > largest_long_profit_trade:
                    largest_long_profit_trade = trade['profit_amount']
            else:
                total_long_loser_trades += 1
                current_result = constants.LOOSE
                consecutive_losses += 1
                if trade['profit_amount'] < largest_long_loss_trade:
                    largest_long_loss_trade = trade['profit_amount']
        
        if current_result != previous_result:
            previous_result = current_result
            if current_result == constants.WIN and consecutive_wins > 1:
                list_consecutive_wins.append(consecutive_wins)
                if consecutive_wins > maximum_consecutive_wins:
                    maximum_consecutive_wins = consecutive_wins
            
            if current_result == constants.LOOSE and consecutive_losses > 1:
                list_consecutive_losses.append(consecutive_losses)
                if consecutive_losses > maximum_consecutive_losses:
                    maximum_consecutive_losses = consecutive_losses
        
        # test if this is the last item in the list. if so, there will be no change in result but 
        # we still have to test for the consecutive wins os losses
        if aux == len(trades_data):
            if current_result == constants.WIN and consecutive_wins > 1:
                list_consecutive_wins.append(consecutive_wins)
                if consecutive_wins > maximum_consecutive_wins:
                    maximum_consecutive_wins = consecutive_wins
            
            if current_result == constants.LOOSE and consecutive_losses > 1:
                list_consecutive_losses.append(consecutive_losses)
                if consecutive_losses > maximum_consecutive_losses:
                    maximum_consecutive_losses = consecutive_losses
            
    df = pd.DataFrame(list_consecutive_wins)
    mean = df.mean().to_dict().get(0)
    average_consecutive_wins = mean if mean != None else 0.0
    
    df = pd.DataFrame(list_consecutive_losses)
    mean = df.mean().to_dict().get(0)
    average_consecutive_losses = mean if mean != None else 0.0

    # Header section    
    asset = simulation_data['asset_under_simulation']
    period_range = f"From: {simulation_data['cycle_start']} To: {simulation_data['cycle_end']} with a frequency: {constants.FREQUENCY[simulation_data['frequency']]}"
    model = f"Orders are sent on market data with the value based on the {parms.PRICES_BASED_ON.upper()} price"
    exposable_percentage = f"Exposing a maximum of {parms.EXPOSABLE_PERCENTAGE}% of the available (current) balance on each trade"
    lot_size = f'{parms.LOT_SIZE} shares/lot'    
    number_of_testing_days = mstore.get("counter_testing_days")
    
    #General View
    initial_balance = simulation_data['initial_balance']
    final_balance = simulation_data['current_balance']
    total_trades = total_short_trades + total_long_trades
    total_winner_trades = total_short_winner_trades + total_long_winner_trades
    total_loser_trades = total_short_loser_trades + total_long_loser_trades
    net_profit = final_balance - initial_balance
    profit_percentage = round(((final_balance / initial_balance - 1) * 100),2)
    
    # Detailed View for Profit and Loss with Short and Long Trades
    # print(f'{gross_profit_short_trades:>15.2f}')
    gross_profit_short_trades = trades.select_trades_sum_profit_amount(simulation_id, constants.SHORT)
    gross_profit_long_trades = trades.select_trades_sum_profit_amount(simulation_id, constants.LONG)
    gross_profit_total = gross_profit_short_trades + gross_profit_long_trades
    
    gross_loss_short_trades = trades.select_trades_sum_loss_amount(simulation_id, constants.SHORT)
    gross_loss_long_trades = trades.select_trades_sum_loss_amount(simulation_id, constants.LONG)
    gross_loss_total = gross_loss_short_trades + gross_loss_long_trades
    
    # getting all the market date used in the simulation to calculate maximum drawdown
    prices = market_data.select_all_market_data_by_period(asset, period[0], period[-1])
    
    peak = prices[0]['high']
    max_drawdown = 0

    for p in prices:
        peak = max(peak, p['high'])
        drawdown = (p['low'] - peak) / peak
        max_drawdown = min(max_drawdown, drawdown)

    max_drawdown = round(max_drawdown, 2)

    output = f'\n'
    output += f'{"-"*60} STRATEGY BACKTESTING - EXECUTION REPORT {"-"*60}\n'
    output += f'\n'
    output += f' Asset Under Simulation ......: {asset}\n'
    output += f' Period ......................: {period_range}\n'
    output += f' Model .......................: {model}\n'
    output += f' Capital Exposed (%) .........: {exposable_percentage}\n'
    output += f' Lot Size ....................: {lot_size}\n'
    output += f' # of trading days analyzed ..: {number_of_testing_days}\n'
    output += f'\n'
    output += f'\n'
    output += f'{"":>15}MAIN RESULTS\n'
    output += f'{"-"*50}'
    output += f'\n'
    output += f' Initial Balance .............: {initial_balance:>15.2f}\n'
    output += f' Final Balance ...............: {final_balance:>15.2f}\n'
    output += f' Net Profit ..................: {net_profit:>15.2f}\n'
    output += f' Profit (%) ..................: {profit_percentage:>15.2f}\n'
    output += f'\n'
    output += f'\n'
    output += f'{"":>15}TRADE STATISTICS{"":>37}SHORT{"":>23}LONG{"":>22}OVERALL\n'
    output += f'{"-"*50}{"":>10}{"-"*19}{"":>9}{"-"*19}{"":>9}{"-"*19}{"":>19}\n'
    output += f' # of Trades Executed .......:{"":>40}{total_short_trades:>8}{"":>20}{total_long_trades:>8}{"":>20}{total_trades:>8}\n'
    output += f' # of Winners ...............:{"":>40}{total_short_winner_trades:>8}{"":>20}{total_long_winner_trades:>8}{"":>20}{total_winner_trades:>8}\n'
    output += f' # of Losers ................:{"":>40}{total_short_loser_trades:>8}{"":>20}{total_long_loser_trades:>8}{"":>20}{total_loser_trades:>8}\n'
    output += f' Gross Profit Trades ........:{"":>40}{gross_profit_short_trades:>8}{"":>20}{gross_profit_long_trades:>8}{"":>20}{gross_profit_total:>8}\n'
    output += f' Gross Loss Trades ..........:{"":>40}{gross_loss_short_trades:>8}{"":>20}{gross_loss_long_trades:>8}{"":>20}{gross_loss_total:>8}\n'
    # output += f'\n'
    # output += f'\n'
    # output += f'{"":>15}OTHER STATISTICS{"":>37}SHORT{"":>23}LONG{"":>23}OVERALL\n'
    # output += f'{"-"*50}{"":>10}{"-"*19}{"":>9}{"-"*19}{"":>9}{"-"*19}{"":>19}\n'
    output += f' Largest Winner Trade .......:{"":>40}{largest_short_profit_trade:>8}{"":>20}{largest_long_profit_trade:>8}{"":>20}{largest_short_profit_trade if largest_short_profit_trade > largest_long_profit_trade else largest_long_profit_trade:>8}\n'
    output += f' Largest Loser Trade ........:{"":>40}{largest_short_loss_trade:>8}{"":>20}{largest_long_loss_trade:>8}{"":>20}{largest_short_loss_trade if largest_short_loss_trade < largest_long_loss_trade else largest_long_loss_trade:>8}\n'
    output += f' Most Consecutive Wins ......:{"":>40}{"--":>8}{"":>20}{"--":>8}{"":>20}{maximum_consecutive_wins:>8}\n'
    output += f' Most Consecutive Losses ....:{"":>40}{"--":>8}{"":>20}{"--":>8}{"":>20}{maximum_consecutive_losses:>8}\n'
    output += f' Avg Consecutive Wins .......:{"":>40}{"--":>8}{"":>20}{"--":>8}{"":>20}{average_consecutive_wins:>8}\n'
    output += f' Avg Consecutive Losses .....:{"":>40}{"--":>8}{"":>20}{"--":>8}{"":>20}{average_consecutive_losses:>8}\n'
    output += f' Maximum Drawdown ...........:{"":>40}{"--":>8}{"":>20}{"--":>8}{"":>20}{max_drawdown:>8}\n'
    print(output)



#     # List of field names
#     fields = [
#         "asset", "period_range", "model", "exposable_percentage", "lot_size", "number_of_testing_days",
#         "initial_balance", "final_balance", "total_trades", "net_profit", "profit_percentage",
#         "total_short_trades", "total_long_trades", "total_short_winner_trades", "total_long_winner_trades",
#         "total_short_loser_trades", "total_long_loser_trades", "largest_short_profit_trade",
#         "largest_long_profit_trade", "largest_short_loss_trade", "largest_long_loss_trade",
#         "consecutive_wins", "consecutive_losses", "maximum_consecutive_wins", "maximum_consecutive_losses",
#         "average_consecutive_wins", "average_consecutive_losses", "max_drawdown",
#         "gross_profit_short_trades", "gross_profit_long_trades", "gross_profit_total",
#         "gross_loss_short_trades", "gross_loss_long_trades", "gross_loss_total"
#     ]
    
#     values = [
#         asset, period_range, model, exposable_percentage, lot_size, number_of_testing_days,
#         initial_balance, final_balance, total_trades, net_profit, profit_percentage,
#         total_short_trades, total_long_trades, total_short_winner_trades, total_long_winner_trades,
#         total_short_loser_trades, total_long_loser_trades, largest_short_profit_trade,
#         largest_long_profit_trade, largest_short_loss_trade, largest_long_loss_trade,
#         consecutive_wins, consecutive_losses, maximum_consecutive_wins, maximum_consecutive_losses,
#         average_consecutive_wins, average_consecutive_losses, max_drawdown,
#         gross_profit_short_trades, gross_profit_long_trades, gross_profit_total,
#         gross_loss_short_trades, gross_loss_long_trades, gross_loss_total
#     ]


#     print_report(fields, values)

# def print_report(field_names, field_values):
#     """
#     Prints a plain-text report using the given field names and values.
#     Both lists must be the same length.
#     """
#     if len(field_names) != len(field_values):
#         print("Error: field names and field values must have the same length.")
#         return

#     print("\n--- Report ---")
#     for name, value in zip(field_names, field_values):
#         print(f"{name}: {value}")
#     print("----------------\n")