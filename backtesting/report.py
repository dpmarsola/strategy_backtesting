from .data import simulation
from .data import trades
from .data import market_data
from . import constants
from . import data_plot
from . import memory_store
import pandas as pd
from datetime import datetime

mstore = memory_store.MermoryStore()
class Report():

    # Header section  
    simulation_id = ""  
    asset = ""
    period_from = ""
    period_to = ""
    frequency = ""
    prices_based_on = ""
    strategy_description = ""
    exposable_cpt = ""
    lot_size = ""
    number_of_testing_days = 0
    
    # Balance and Profit Margin
    initial_balance = 0
    final_balance = 0
    net_profit = 0
    profit_percentage = 0
    
    # Totals
    total_short_trades = 0
    total_long_trades = 0
    total_trades = 0
    total_short_winner_trades = 0
    total_long_winner_trades = 0
    total_winner_trades = 0
    total_short_loser_trades = 0
    total_long_loser_trades = 0
    total_loser_trades = 0

    # Gross Profits and Losses
    gross_profit_short_trades = 0
    gross_profit_long_trades = 0
    gross_profit_total = 0
    gross_loss_short_trades = 0
    gross_loss_long_trades = 0
    gross_loss_total = 0
    
    # Largest Profits and Losses
    largest_short_profit_trade = 0
    largest_long_profit_trade = 0
    largest_overall_profit_trade = 0
    largest_short_loss_trade = 0
    largest_long_loss_trade = 0
    largest_overall_loss_trade = 0
    
    # Miscellanea 
    consecutive_wins = 0
    consecutive_losses = 0
    maximum_consecutive_wins = 0
    maximum_consecutive_losses = 0
    average_consecutive_wins = 0
    average_consecutive_losses = 0
    
    #Drawdown
    max_drawdown = 0

    # Auxiliary varibales for calculations    
    previous_result = ""
    current_result = ""
    aux = 0
    list_consecutive_wins = []
    list_consecutive_losses = []
    
    
    def __init__(self, simulation_id: str, period: str, error_message: str):
        
        # getting the data need from the tables
        self.simulation_data = simulation.select_simulation_data_by_id(simulation_id)
        self.trades_data = trades.select_trades_data_by_simulation_id(simulation_id)
        self.error_message = error_message
                
        # Header section    
        self.simulation_id = self.simulation_data['simulation_id']
        self.asset = self.simulation_data['asset_under_simulation']
        self.period_from = self.simulation_data['cycle_start']
        self.period_to = self.simulation_data['cycle_end']
        self.frequency = self.simulation_data['frequency']
        self.prices_based_on = mstore.get(constants.PRICES_BASED_ON).upper()
        self.strategy_description = mstore.get("strategy").description
        self.exposable_cpt = mstore.get(constants.EXPOSABLE_PERCENTAGE)
        self.lot_size = mstore.get(constants.LOT_SIZE)
        self.number_of_testing_days = mstore.get("counter_testing_days")

        # getting all the market date used in the simulation to calculate maximum drawdown
        self.prices = market_data.select_all_market_data_by_period(self.asset, period[0], period[-1])
        
        if len(self.trades_data) == 0:
            self.error_message = f'No data available for {self.simulation_data["asset_under_simulation"]}'
        
        if not self.error_message:
            previous_result  = ''
            for trade in self.trades_data:
                self.aux += 1

                if trade['position_type'] == constants.SHORT:
                    self.total_short_trades += 1
                    if trade['profit_amount'] >= 0:
                        self.total_short_winner_trades += 1
                        current_result = constants.WIN
                        if trade['profit_amount'] > self.largest_short_profit_trade:
                            self.largest_short_profit_trade = trade['profit_amount']
                    else:
                        self.total_short_loser_trades += 1
                        current_result = constants.LOOSE
                        if trade['profit_amount'] < self.largest_short_loss_trade:
                            self.largest_short_loss_trade = trade['profit_amount']
                
                if trade['position_type'] == constants.LONG:
                    self.total_long_trades += 1
                    if trade['profit_amount'] >= 0:
                        self.total_long_winner_trades += 1
                        current_result = constants.WIN
                        if trade['profit_amount'] > self.largest_long_profit_trade:
                            self.largest_long_profit_trade = trade['profit_amount']
                    else:
                        self.total_long_loser_trades += 1
                        current_result = constants.LOOSE
                        if trade['profit_amount'] < self.largest_long_loss_trade:
                            self.largest_long_loss_trade = trade['profit_amount']
                
                if current_result != previous_result:
                    if previous_result == constants.WIN and self.consecutive_wins > 1:
                        self.list_consecutive_wins.append(self.consecutive_wins)
                    if previous_result == constants.LOOSE and self.consecutive_losses > 1:
                        self.list_consecutive_losses.append(self.consecutive_losses)
                    previous_result = current_result
                    self.consecutive_wins = 0
                    self.consecutive_losses = 0
                else:
                    if current_result == constants.WIN:
                        self.consecutive_wins += 1
                    else:
                        self.consecutive_losses += 1
                                                                
                # test if this is the last item in the list. if so, there will be no change in result but 
                # we still have to test for the consecutive wins os losses
                if self.aux == len(self.trades_data):
                    if current_result == constants.WIN:
                        self.list_consecutive_wins.append(self.consecutive_wins)
                        if self.consecutive_wins > self.maximum_consecutive_wins:
                            self.maximum_consecutive_wins = self.consecutive_wins
                    
                    if current_result == constants.LOOSE:
                        self.list_consecutive_losses.append(self.consecutive_losses)
                        if self.consecutive_losses > self.maximum_consecutive_losses:
                            self.maximum_consecutive_losses = self.consecutive_losses

            self.largest_overall_profit_trade = self.largest_short_profit_trade if self.largest_short_profit_trade > self.largest_long_profit_trade else self.largest_long_profit_trade
            self.largest_overall_loss_trade = self.largest_short_loss_trade if self.largest_short_loss_trade < self.largest_long_loss_trade else self.largest_long_loss_trade
            
            df = pd.DataFrame(self.list_consecutive_wins)
            if df.size > 0:
                mean = df.mean().to_dict().get(0)
                self.maximum_consecutive_wins = df.max().to_dict()[0]
                self.average_consecutive_wins = mean if mean != None else 0.0
            
            df = pd.DataFrame(self.list_consecutive_losses)
            if df.size > 0:
                mean = df.mean().to_dict().get(0)
                self.maximum_consecutive_losses = df.max().to_dict()[0]
                self.average_consecutive_losses = mean if mean != None else 0.0

            #General View
            self.initial_balance = self.simulation_data['initial_balance']
            self.final_balance = self.simulation_data['current_balance']
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
            
            peak = self.prices[0]['high']

            for p in self.prices:
                peak = max(peak, p['high'])
                drawdown = (p['low'] - peak) / peak
                self.max_drawdown = min(self.max_drawdown, drawdown)

            self.max_drawdown = round(self.max_drawdown, 2)
            
            # Begining of the logic to send data to be plotted by mathplotlib
            datetimes = []
            for i in self.prices:
                datetimes.append(i['datetime'])
                        
            self.mplot_market_and_trades_data = pd.DataFrame(self.prices, index=datetimes)
            self.mplot_market_and_trades_data['trade_open_close_indicator'] = None
            self.mplot_market_and_trades_data['trade_short_or_long_indicator'] = None
            self.mplot_market_and_trades_data['trade_open_price'] = None
            self.mplot_market_and_trades_data['trade_close_price'] = None

            for trade in self.trades_data:
                format_string = "%d-%m-%Y %H:%M:%S"
                trade_open_date_ddmmYYYY = datetime.strptime(trade['trade_open_date'], format_string)
                trade_open_date_YYYYmmdd = trade_open_date_ddmmYYYY.strftime('%Y-%m-%d %H:%M:%S')
                self.mplot_market_and_trades_data.loc[ trade_open_date_YYYYmmdd, 'trade_open_close_indicator' ] = "open"
                self.mplot_market_and_trades_data.loc[ trade_open_date_YYYYmmdd, 'trade_short_or_long_indicator' ] = trade['position_type']
                self.mplot_market_and_trades_data.loc[ trade_open_date_YYYYmmdd, 'trade_open_price' ] = trade['position_amount']/trade['position_quantity']
                
                
                trade_close_date_ddmmYYYY = datetime.strptime(trade['trade_close_date'], format_string)
                trade_close_date_YYYYmmdd = trade_close_date_ddmmYYYY.strftime('%Y-%m-%d %H:%M:%S')
                self.mplot_market_and_trades_data.loc[ trade_close_date_YYYYmmdd, 'trade_open_close_indicator' ] = "close"
                self.mplot_market_and_trades_data.loc[ trade_close_date_YYYYmmdd, 'trade_short_or_long_indicator' ] = trade['position_type']
                self.mplot_market_and_trades_data.loc[ trade_close_date_YYYYmmdd, 'trade_close_price' ] = trade['trade_close_amount']/trade['position_quantity']
                
            self.mplot_market_and_trades_data = self.mplot_market_and_trades_data.set_index('datetime')
        
    def send_to_stdout(self):

        # Header section
        self.text_period = f"From: {self.simulation_data['cycle_start']} To: {self.simulation_data['cycle_end']}"
        self.text_price_considered = f"Positions are opened and closed based on the {self.prices_based_on.upper()} price"
        self.text_exposable_cpt = f"Exposing a maximum of {self.exposable_cpt} % of the available (current) balance on each trade"
        self.text_frequency =  f"{constants.FREQUENCY[self.frequency]}"
        
        output = f'\n'
        output += f'{"-"*161}\n'
        output += f'{"-"*60} STRATEGY BACKTESTING - EXECUTION REPORT {"-"*60}\n'
        output += f'{"-"*161}\n'
        output += f'\n'
        output += f' Simulation ID ...............: {self.simulation_id}\n'
        output += f' Asset Under Simulation ......: {self.asset}\n'
        output += f' Period ......................: {self.text_period}\n'
        output += f' Frequency ...................: {self.text_frequency}\n'
        output += f' Price Considered ............: {self.text_price_considered}\n'
        output += f' Strategy Description ........: {self.strategy_description}\n'
        output += f' Capital Exposed (%) .........: {self.text_exposable_cpt}\n'
        output += f' Lot Size ....................: {self.lot_size} shares/lot\n'
        output += f' # of trading days analyzed ..: {self.number_of_testing_days}\n'
        output += f'\n'
        output += f'\n'
        
        if self.error_message:
            output += f' ERROR DURING SIMULATION .....: {self.error_message}\n'
            output += f'\n'
        else:                    
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
            output += f' Largest Winner Trade .......:{"":>38}{self.largest_short_profit_trade:>8.2f}{"":>20}{self.largest_long_profit_trade:>8.2f}{"":>20}{self.largest_overall_profit_trade:>8.2f}\n'
            output += f' Largest Loser Trade ........:{"":>38}{self.largest_short_loss_trade:>8.2f}{"":>20}{self.largest_long_loss_trade:>8.2f}{"":>20}{self.largest_overall_loss_trade:>8.2f}\n'
            output += f' Most Consecutive Wins ......:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.maximum_consecutive_wins:>8}\n'
            output += f' Most Consecutive Losses ....:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.maximum_consecutive_losses:>8}\n'
            output += f' Avg Consecutive Wins .......:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.average_consecutive_wins:>8.2f}\n'
            output += f' Avg Consecutive Losses .....:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.average_consecutive_losses:>8.2f}\n'
            output += f' Maximum Drawdown ...........:{"":>38}{"--":>8}{"":>20}{"--":>8}{"":>20}{self.max_drawdown:>8.2f}\n'
        print(output)
    
    def plot_chart(self):
        
        dplot = data_plot.DataPlot()
        dplot.execute(self.mplot_market_and_trades_data)

    def send_to_csv(self):
                
        data = {
            # Header section    
            "simulationa_id": self.simulation_id,
            "asset": self.asset,
            "period_from": self.period_from,
            "period_to": self.period_to,
            "frequency": self.frequency,
            "prices_based_on": self.prices_based_on,
            "text_exposable_cpt": self.exposable_cpt,
            "lot_size": self.lot_size,
            "number_of_testing_days": self.number_of_testing_days,
            
            # Balance and Profit Margin
            "initial_balance": self.initial_balance,
            "final_balance": self.final_balance,
            "net_profit": self.net_profit,
            "profit_percentage": self.profit_percentage,
            
            # Totals
            "total_short_trades": self.total_short_trades,
            "total_long_trades": self.total_long_trades,
            "total_trades": self.total_trades,
            "total_short_winner_trades": self.total_short_winner_trades,
            "total_long_winner_trades": self.total_long_winner_trades,
            "total_winner_trades": self.total_winner_trades,
            "total_short_loser_trades": self.total_short_loser_trades,
            "total_long_loser_trades": self.total_long_loser_trades,
            "total_loser_trades": self.total_loser_trades,
            
            # Gross Profits and Losses
            "gross_profit_short_trades": self.gross_profit_short_trades,
            "gross_profit_long_trades": self.gross_profit_long_trades,
            "gross_profit_total": self.gross_profit_total,
            "gross_loss_short_trades": self.gross_loss_short_trades,
            "gross_loss_long_trades": self.gross_loss_long_trades,
            "gross_loss_total": self.gross_loss_total,
            
            # Largest Profits and Losses
            "largest_short_profit_trade": self.largest_short_profit_trade,
            "largest_long_profit_trade": self.largest_long_profit_trade,
            "largest_overall_profit_trade": self.largest_overall_profit_trade,
            "largest_short_loss_trade": self.largest_short_loss_trade,
            "largest_long_loss_trade": self.largest_long_loss_trade,
            "largest_overall_loss_trade": self.largest_overall_loss_trade,
            
            # Miscellanea 
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "maximum_consecutive_wins": self.maximum_consecutive_wins,
            "maximum_consecutive_losses": self.maximum_consecutive_losses,
            "average_consecutive_wins": self.average_consecutive_wins,
            "average_consecutive_losses": self.average_consecutive_losses,
            
            # Drawdown
            "max_drawdown": self.max_drawdown,
        }
        
        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Save to CSV
        df.to_csv(mstore.get(constants.OUTPUT_FILE), index=False)

        print("✅ Saved trading stats to trading_stats.csv")        