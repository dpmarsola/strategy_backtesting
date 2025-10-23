class EveryEvenDay():
    
    description = 'Uses a simple useless model where every even day is a singal to get in and every odd day a signal to get out! :('
    
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