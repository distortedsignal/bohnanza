# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 22:20:42 2018

@author: David Kelley, 2018
"""

from multiprocessing import Pool

from game import Game, Strategy

class NaiveStrategy(Strategy):
    """Example class for player strategy. This player does not trade.
    
    To be expanded later with trading. 
    """
    
    def __init__(self, seat):
        self.name = "Autarky" 
        
    def plant_from_hand(self, player):
        """Specify which card goes in which field, in order."""
        if len(player.hand) == 0: 
            plants = []
            field_to_plant = []
            return [field_to_plant, plants]
        
        plants = [player.hand[0]] 
        if len(player.fields[1]) == 0 or player.hand[0] == player.fields[1][0]:
            fields_to_plant = [1]
        else:
            fields_to_plant = [0]
            
        return [fields_to_plant, plants]

    def plant_from_trade(self, player, cards): 
        """Specify which card goes in which field, in order."""
        if len(cards) == 0: 
            field_to_plant = []
            return [field_to_plant, cards]
        
        fields_to_plant = []
        for iCard in cards:
            if len(player.fields[1]) == 0 or cards[0] == player.fields[1][0]:
                fields_to_plant.append(1)
            else:
                fields_to_plant.append(0)
            
        return [fields_to_plant, cards]
        pass

    def trade(self, player, game, cards): 
        pass
        
       
def simulate(nPlayers):
    g = Game([NaiveStrategy(i) for i in range(nPlayers)])
    return g.run()

def f(x):
    return simulate(3)

if __name__ == "__main__":
    pool = Pool()

    points = pool.map(f, range(5000))
    
    avg = [sum([p[i] for p in points])/len(points) for i in range(len(points[0]))]
    print(avg)
