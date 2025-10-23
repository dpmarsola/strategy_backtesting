import backtesting.simulate as sim

class Strategy():
    def signal_in(self, period):
        
        if int(period.strftime("%d")) % 2 != 0:
            position_type = "short"
            decision = "get_in"
        else:
            position_type = "long"
            decision = "stay"
        
        return decision, position_type

    def signal_out(self, period):
        
        if int(period.strftime("%d")) % 2 == 0:
            decision = "get_out"
        else:
            decision = "stay"
            
        return decision    
    # counter_in = {'count': 0, 'position' : None, 'decision' : None }
    # counter_out = {'count': 0, 'position' : None, 'decision' : None }
        
    # def signal_in(self, period):
        
    #     import random
    #     random_integer = random.randint(1, 10)
        
    #     if random_integer % 2 == 0:
    #         position_type = "short"
    #     else:
    #         position_type = "long"

    #     random_integer = random.randint(1, 10)
    #     if random_integer % 2 == 0:
    #         decision = "get_in"
    #     else:
    #         decision = "stay"

    #     return decision, position_type

    # def signal_out(self, period):
        
    #     import random
    #     random_integer = random.randint(1, 10)

    #     if random_integer % 2 == 0:
    #         decision = "get_out"
    #     else:
    #         decision = "stay"
                 
    #     return decision
    

start_date = '2025-08-01'
end_date = '2025-08-10'
frequency = 'D'
asset = "ITSA4"
initial_balance = 10000.00
exposable_percentage = "100"
lot_size = 100
prices_based_on = "open"
close_on_last_day = True
output_file = 'simu.csv'

sim.register_strategy(Strategy())
sim.simulate(start_date, end_date, frequency, asset, initial_balance, exposable_percentage=exposable_percentage, lot_size=lot_size, prices_based_on=prices_based_on, close_on_last_day=close_on_last_day, output_file=None)