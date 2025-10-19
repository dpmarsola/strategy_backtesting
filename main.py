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
    

start_date = '2025-08-01'
end_date = '2025-08-10'
frequency = 'D'
asset = "ITSA4"
initial_balance = 10000.00

sim.simulate(start_date, end_date, frequency, asset, initial_balance, Strategy())