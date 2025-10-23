from .data import simulation
from .data import trades
from .data import market_data
from . import constants
from . import parms
from . import memory_store
import pandas as pd

mstore = memory_store.MermoryStore()
class Report():

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
    initial_balance = 0
    final_balance = 0
    net_profit = 0
    profit_percentage = 0
    total_trades = 0
    total_winner_trades = 0
    total_loser_trades = 0

    # auxiliary varibales for calculations    
    previous_result = ""
    current_result = ""
    aux = 0
    list_consecutive_wins = []
    list_consecutive_losses = []
    
    # Header section    
    asset = ""
    period_range = ""
    frequency = ""
    model = ""
    exposable_percentage = ""
    lot_size = ""
    number_of_testing_days = 0

    gross_profit_short_trades = 0
    gross_profit_long_trades = 0
    gross_profit_total = 0
    gross_loss_short_trades = 0
    gross_loss_long_trades = 0
    gross_loss_total = 0
        
    def send_to_stdout(self, simulation_id: str, period: str, error_message: str):
        
        # getting the data need from the tables
        simulation_data = simulation.select_simulation_data_by_id(simulation_id)
        trades_data = trades.select_trades_data_by_simulation_id(simulation_id)
        
        if len(trades_data) == 0:
            error_message = f'No data available for {simulation_data["asset_under_simulation"]}'
            
        # Header section    
        self.asset = simulation_data['asset_under_simulation']
        self.period_range = f"From: {simulation_data['cycle_start']} To: {simulation_data['cycle_end']}"
        self.frequency = f"{constants.FREQUENCY[simulation_data['frequency']]}"
        self.model = f"Orders are sent on market data with the value based on the {mstore.get(constants.PRICES_BASED_ON).upper()} price"
        self.exposable_percentage = f"Exposing a maximum of {mstore.get(constants.EXPOSABLE_PERCENTAGE)}% of the available (current) balance on each trade"
        self.lot_size = f'{mstore.get(constants.LOT_SIZE)} shares/lot'    
        self.number_of_testing_days = mstore.get("counter_testing_days")

        
        output = f'\n'
        output += f'{"-"*161}\n'
        output += f'{"-"*60} STRATEGY BACKTESTING - EXECUTION REPORT {"-"*60}\n'
        output += f'{"-"*161}\n'
        output += f'\n'
        output += f' Asset Under Simulation ......: {self.asset}\n'
        output += f' Period ......................: {self.period_range}\n'
        output += f' Frequency ...................: {self.frequency}\n'
        output += f' Model .......................: {self.model}\n'
        output += f' Capital Exposed (%) .........: {self.exposable_percentage}\n'
        output += f' Lot Size ....................: {self.lot_size}\n'
        output += f' # of trading days analyzed ..: {self.number_of_testing_days}\n'
        output += f'\n'
        output += f'\n'
        
        if error_message:
            output += f' ERROR DURING SIMULATION .....: {error_message}\n'
            output += f'\n'
        else:

            for trade in trades_data:
                self.aux += 1
                
                if trade['position_type'] == constants.SHORT:
                    self.total_short_trades += 1
                    if trade['profit_amount'] >= 0:
                        self.total_short_winner_trades += 1
                        current_result = constants.WIN
                        self.consecutive_wins += 1
                        if trade['profit_amount'] > self.largest_short_profit_trade:
                            self.largest_short_profit_trade = trade['profit_amount']
                    else:
                        self.total_short_loser_trades += 1
                        current_result = constants.LOOSE
                        self.consecutive_losses += 1
                        if trade['profit_amount'] < self.largest_short_loss_trade:
                            self.largest_short_loss_trade = trade['profit_amount']
                
                if trade['position_type'] == constants.LONG:
                    self.total_long_trades += 1
                    if trade['profit_amount'] >= 0:
                        self.total_long_winner_trades += 1
                        current_result = constants.WIN
                        self.consecutive_wins += 1
                        if trade['profit_amount'] > self.largest_long_profit_trade:
                            self.largest_long_profit_trade = trade['profit_amount']
                    else:
                        self.total_long_loser_trades += 1
                        current_result = constants.LOOSE
                        self.consecutive_losses += 1
                        if trade['profit_amount'] < self.largest_long_loss_trade:
                            self.largest_long_loss_trade = trade['profit_amount']
                
                if current_result != self.previous_result:
                    self.previous_result = current_result
                    if current_result == constants.WIN and self.consecutive_wins > 1:
                        self.list_consecutive_wins.append(self.consecutive_wins)
                        if self.consecutive_wins > self.maximum_consecutive_wins:
                            self.maximum_consecutive_wins = self.consecutive_wins
                    
                    if current_result == constants.LOOSE and self.consecutive_losses > 1:
                        self.list_consecutive_losses.append(self.consecutive_losses)
                        if self.consecutive_losses > self.maximum_consecutive_losses:
                            self.maximum_consecutive_losses = self.consecutive_losses
                
                # test if this is the last item in the list. if so, there will be no change in result but 
                # we still have to test for the consecutive wins os losses
                if self.aux == len(trades_data):
                    if current_result == constants.WIN and self.consecutive_wins > 1:
                        self.list_consecutive_wins.append(self.consecutive_wins)
                        if self.consecutive_wins > self.maximum_consecutive_wins:
                            self.maximum_consecutive_wins = self.consecutive_wins
                    
                    if current_result == constants.LOOSE and self.consecutive_losses > 1:
                        self.list_consecutive_losses.append(self.consecutive_losses)
                        if self.consecutive_losses > self.maximum_consecutive_losses:
                            self.maximum_consecutive_losses = self.consecutive_losses
                    
            df = pd.DataFrame(self.list_consecutive_wins)
            mean = df.mean().to_dict().get(0)
            self.average_consecutive_wins = mean if mean != None else 0.0
            
            df = pd.DataFrame(self.list_consecutive_losses)
            mean = df.mean().to_dict().get(0)
            self.average_consecutive_losses = mean if mean != None else 0.0

            #General View
            self.initial_balance = simulation_data['initial_balance']
            self.final_balance = simulation_data['current_balance']
            self.total_trades = self.total_short_trades + self.total_long_trades
            self.total_winner_trades = self.total_short_winner_trades + self.total_long_winner_trades
            self.total_loser_trades = self.total_short_loser_trades + self.total_long_loser_trades
            self.net_profit = self.final_balance - self.initial_balance
            self.profit_percentage = round(((self.final_balance / self.initial_balance - 1) * 100),2)
            
            # Detailed View for Profit and Loss with Short and Long Trades
            # print(f'{self.gross_profit_short_trades:>15.2f}')
            self.gross_profit_short_trades = trades.select_trades_sum_profit_amount(simulation_id, constants.SHORT)
            self.gross_profit_long_trades = trades.select_trades_sum_profit_amount(simulation_id, constants.LONG)
            self.gross_profit_total = self.gross_profit_short_trades + self.gross_profit_long_trades
            
            self.gross_loss_short_trades = trades.select_trades_sum_loss_amount(simulation_id, constants.SHORT)
            self.gross_loss_long_trades = trades.select_trades_sum_loss_amount(simulation_id, constants.LONG)
            self.gross_loss_total = self.gross_loss_short_trades + self.gross_loss_long_trades
            
            # getting all the market date used in the simulation to calculate maximum drawdown
            prices = market_data.select_all_market_data_by_period(self.asset, period[0], period[-1])
            
            peak = prices[0]['high']
            max_drawdown = 0

            for p in prices:
                peak = max(peak, p['high'])
                drawdown = (p['low'] - peak) / peak
                max_drawdown = min(max_drawdown, drawdown)

            max_drawdown = round(max_drawdown, 2)
            
            output += f'{"":>15}MAIN RESULTS\n'
            output += f'{"-"*50}'
            output += f'\n'
            output += f' Initial Balance .............: {self.initial_balance:>15.2f}\n'
            output += f' Final Balance ...............: {self.final_balance:>15.2f}\n'
            output += f' Net Profit ..................: {self.net_profit:>15.2f}\n'
            output += f' Profit (%) ..................: {self.profit_percentage:>15.2f}\n'
            output += f'\n'
            output += f'\n'
            output += f'{"":>15}TRADE STATISTICS{"":>37}SHORT{"":>23}LONG{"":>22}OVERALL\n'
            output += f'{"-"*50}{"":>10}{"-"*19}{"":>9}{"-"*19}{"":>9}{"-"*19}{"":>19}\n'
            output += f' # of Trades Executed .......:{"":>38}{self.total_short_trades:>8}{"":>20}{self.total_long_trades:>8}{"":>20}{self.total_trades:>8}\n'
            output += f' # of Winners ...............:{"":>38}{self.total_short_winner_trades:>8}{"":>20}{self.total_long_winner_trades:>8}{"":>20}{self.total_winner_trades:>8}\n'
            output += f' # of Losers ................:{"":>38}{self.total_short_loser_trades:>8}{"":>20}{self.total_long_loser_trades:>8}{"":>20}{self.total_loser_trades:>8}\n'
            output += f' Gross Profit Trades ........:{"":>38}{self.gross_profit_short_trades:>8.2f}{"":>20}{self.gross_profit_long_trades:>8.2f}{"":>20}{self.gross_profit_total:>8.2f}\n'
            output += f' Gross Loss Trades ..........:{"":>38}{self.gross_loss_short_trades:>8.2f}{"":>20}{self.gross_loss_long_trades:>8.2f}{"":>20}{self.gross_loss_total:>8.2f}\n'
            # output += f'\n'
            # output += f'\n'
            # output += f'{"":>15}OTHER STATISTICS{"":>37}SHORT{"":>23}LONG{"":>23}OVERALL\n'
            # output += f'{"-"*50}{"":>10}{"-"*19}{"":>9}{"-"*19}{"":>9}{"-"*19}{"":>19}\n'
            output += f' Largest Winner Trade .......:{"":>38}{self.largest_short_profit_trade:>8.2f}{"":>20}{self.largest_long_profit_trade:>8.2f}{"":>20}{self.largest_short_profit_trade if self.largest_short_profit_trade > self.largest_long_profit_trade else self.largest_long_profit_trade:>8.2f}\n'
            output += f' Largest Loser Trade ........:{"":>38}{self.largest_short_loss_trade:>8.2f}{"":>20}{self.largest_long_loss_trade:>8.2f}{"":>20}{self.largest_short_loss_trade if self.largest_short_loss_trade < self.largest_long_loss_trade else self.largest_long_loss_trade:>8.2f}\n'
            output += f' Most Consecutive Wins ......:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.maximum_consecutive_wins:>8}\n'
            output += f' Most Consecutive Losses ....:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.maximum_consecutive_losses:>8}\n'
            output += f' Avg Consecutive Wins .......:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.average_consecutive_wins:>8.2f}\n'
            output += f' Avg Consecutive Losses .....:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.average_consecutive_losses:>8.2f}\n'
            output += f' Maximum Drawdown ...........:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{max_drawdown:>8.2f}\n'
        print(output)

    def send_to_csv(self):
        
        output_file = mstore.get(constants.OUTPUT_FILE)
        with open(output_file, "w") as f:
            output = 'asset,'
            
            f.write(output)
        