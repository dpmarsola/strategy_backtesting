from . import constants
from .data import simulation
from .data import trades
from . import decision_helper
from . import parms
from . import memory_store

mstore = memory_store.MermoryStore()
dhelper = decision_helper.Decision_Helper()
class Operate():
    
    def send_order(self, order_typ, simulation_id, position_quantity, position_type, amount, asset, price, period):
                
        effective_amount = price * position_quantity
        effective_quantity = position_quantity

        return effective_amount, effective_quantity
             
    def open_position(self, simulation_id, current_date, asset, asset_current_market_price, position_type):
        
        # determine the position_quantity and then execute a buy or sell operation
        exposed_amount = dhelper.determine_amount_to_expose(simulation_id)
        
        # given the amount to be exposed, determine the maximum quantity that is possible to operate under current market price of this asset
        max_quantity_possible = exposed_amount // asset_current_market_price
        lot_size = mstore.get(constants.LOT_SIZE)
        
        # If the maximum possible quantity is less than 1 LOT_SIZE then this position cannot be opened.
        if lot_size > max_quantity_possible:
            raise ValueError(f"Amount exposed {exposed_amount} is too low to buy the minimun lot size ({lot_size}) at the current value of the asset ({asset_current_market_price}) on date ({current_date.strftime('%d-%m-%Y')}).")

        # Now make this possible quantity fit as a multiple of the LOT_SIZE and get rid of the excess
        excess_quantity = max_quantity_possible % lot_size
        max_quantity_possible = max_quantity_possible - excess_quantity
        fitted_amount = asset_current_market_price * max_quantity_possible
                
        if position_type == constants.LONG:
            order_type = constants.BUY
            subtract_it = True
            effective_amount, effective_quantity = self.send_order(order_type, simulation_id, max_quantity_possible, position_type, fitted_amount, asset, asset_current_market_price, current_date)
        else:
            order_type = constants.SELL
            subtract_it = False
            effective_amount, effective_quantity = self.send_order(order_type, simulation_id, max_quantity_possible, position_type, fitted_amount, asset, asset_current_market_price, current_date)
        
        if effective_amount > 0:
            # debit from simulation's current_position
            simulation.update_simulation_current_balance(simulation_id, effective_amount, subtract_it)
            # add a trade to the trades history
            trades.insert_trades_data(current_date, simulation_id, asset, position_type, effective_amount, effective_quantity, constants.ZERO, constants.ZERO, constants.ZERO, constants.ZERO)
 
    def close_position(self, simulation_id, current_date, trade, asset, asset_current_market_price):
        
        if trade['position_type'] == constants.LONG:
            order_type = constants.SELL
            subtract_it = False
            effective_amount, effective_quantity = self.send_order(order_type, simulation_id, trade['position_quantity'], trade['position_type'], trade['position_amount'], asset, asset_current_market_price, current_date)
        else:
            order_type = constants.BUY
            subtract_it = True
            effective_amount, effective_quantity = self.send_order(order_type, simulation_id, trade['position_quantity'], trade['position_type'], trade['position_amount'], asset, asset_current_market_price, current_date)
            
        if effective_amount > 0:
            # credit simulation's current_position
            simulation.update_simulation_current_balance(simulation_id, effective_amount, subtract_it)
            # calculate the profit or loss and update in trades history
            trade_close_date = current_date
            trade_close_amount = effective_amount
            if subtract_it:
                profit_amount = trade['position_amount'] - trade_close_amount
                profit_percentage = ((trade['position_amount'] / trade_close_amount) - 1) * 100
            else:
                profit_amount = trade_close_amount - trade['position_amount']
                profit_percentage = ((trade_close_amount / trade['position_amount']) - 1) * 100
            trades.update_account_position_balance(simulation_id, trade['trade_open_date'], trade_close_date, trade_close_amount, profit_amount, profit_percentage)