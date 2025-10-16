from .data import simulation as sim
from .data import account_position as acc
from .data import market_data as mkt
from . import parms
from . import constants


class Information():
    
    flag = True
    position_type = ""
    position_amount = 0
    position_quantity = 0

    def check_status_positioned(self, simulation_id):
        
        result = {"positioned" : False,
                  "position_amount" : 0,
                  "position_type" : constants.NA}

        _,_,self.position_type,self.position_amount,self.position_quantity,_ = acc.select_account_position_data_by_simulation_id(simulation_id)    
        
        if self.position_type != constants.NA:
            result["position_amount"] = self.position_amount
            result["position_type"] = self.position_type
            result["position_quantity"] = self.position_quantity
            result["positioned"] = True

        return result 

    def determine_amount_to_expose(self, simulation_id):
        
        _,_,_,_,_,_,current_balance = sim.select_simulation_data_by_id(simulation_id)
        
        exposable_amount = current_balance * (int(parms.EXPOSABLE_PERCENTAGE)) // 100
        
        return exposable_amount
    
    def get_position_information(self, simulation_id):
        
        _,_,position_type,exposed_amount,position_quantity,_ = acc.select_account_position_data_by_simulation_id(simulation_id)
        
        return (position_type, exposed_amount, position_quantity)
    
    def get_asset_current_market_price(self, asset, period):
        
        try:
            market_price = mkt.select_market_data_by_period(asset, period)
           
            open = market_price[1]
            high = market_price[2]
            low = market_price[3]
            close = market_price[4]
            
            return (open, high, low, close)
        except Exception as e:
            return None, None, None, None
            