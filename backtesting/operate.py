from . import constants
from .data import simulation as sim
from .data import account_position as acc
from . import decision_helper as dh
from . import parms

dhelper = dh.Decision_Helper()
class Operate():
    
    def send_buy_order(self, simulation_id, position_quantity, position_type, amount, asset, period):
                
        open, high, low, close = dhelper.get_asset_current_market_price(asset, period)
        
        if open == None:
            return 0,0
        
        effective_amount = open * position_quantity
        effective_quantity = position_quantity

        return effective_amount, effective_quantity
 
            
    def send_sell_order(self, simulation_id, position_quantity, position_type, amount, asset, period):
                
        open, high, low, close = dhelper.get_asset_current_market_price(asset, period)
        
        if open == None:
            return 0,0
        
        effective_amount = open * position_quantity
        effective_quantity = position_quantity

        return effective_amount, effective_quantity
            
    def open_position(self, simulation_id, period, asset, position_type):
        
        # determine the position_quantity and then execute a buy or sell operation
        exposed_amount = dhelper.determine_amount_to_expose(simulation_id)
        asset_current_market_price,_,_,_ = dhelper.get_asset_current_market_price(asset, period)
        
        if asset_current_market_price == None:
            return 0
        else:
            # given the amount to be exposed, determine the maximum quantity that is possible to operate under current market price of this asset
            max_quantity_possible = exposed_amount // asset_current_market_price
            
            # If the maximum possible quantity is less than 1 LOT_SIZE then this position cannot be opened.
            if parms.LOT_SIZE > max_quantity_possible:
                raise ValueError(f"Amount exposed {exposed_amount} is too low and inssuficient to buy the minimun lot size ({parms.LOT_SIZE}) at the current value of the asset ({asset_current_market_price})")

            # Now make this possible quantity fit as a multiple of the LOT_SIZE and get rid of the excess
            excess_quantity = max_quantity_possible % parms.LOT_SIZE
            max_quantity_possible = max_quantity_possible - excess_quantity
            fitted_amount = asset_current_market_price * max_quantity_possible
                    
            if position_type == constants.LONG:
                effective_amount, effective_quantity = self.send_buy_order(simulation_id, max_quantity_possible, position_type, fitted_amount, asset, period)
            else:
                effective_amount, effective_quantity = self.send_sell_order(simulation_id, max_quantity_possible, position_type, fitted_amount, asset, period)
            
            if effective_amount > 0:
                # debit from simulation's current_position
                sim.update_simulation_current_balance(simulation_id, effective_amount, True)
                # add position and position_type to account_position's
                acc.update_account_position_balance(simulation_id, effective_amount, position_type, effective_quantity)
 
    def close_position(self, simulation_id, period, asset):
        
        position_type, exposed_amount, position_quantity = dhelper.get_position_information(simulation_id)
                
        if position_type == constants.LONG:
            effective_amount, effective_quantity = self.send_sell_order(simulation_id, position_quantity, position_type, exposed_amount, asset, period)
        else:
            effective_amount, effective_quantity = self.send_buy_order(simulation_id, position_quantity, position_type, exposed_amount, asset, period)
            
        if effective_amount > 0:
            # cretid simulation's current_position
            sim.update_simulation_current_balance(simulation_id, effective_amount, False)
            # initialize the position information in account_position's
            initial_amount = constants.ZERO
            initial_position_type = constants.NA
            initial_position_quantity = constants.ZERO            
            acc.update_account_position_balance(simulation_id, initial_amount, initial_position_type, initial_position_quantity)