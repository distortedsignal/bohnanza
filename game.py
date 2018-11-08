"""
An implementation of Bohnanza

@author: David Kelley, 2018
"""

import random 

class Card: 
    """Card Object
    Name  and point thresholds are the only properties. The point thresholds 
    are organized the way they are on the card - to get 1 point, you need the
    number of cards listed first in the point_thresholds, 2 for the 2nd, ... 
    """
    types = {'black':[2, 2, 3], 'pinto': [3, 6, 8], 'chili': [3, 5, 5, 8]}
    
    def __init__(self,name):
        self.name = name
        self.point_thresholds = self.types[self.name]
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, card2):
        return self.name == card2.name
    
class Deck:  
    
    types = {'black': 12, 'pinto': 64, 'chili': 48}
    
    def __init__(self): 
        cards = [Card(name) for name in 
                 self.types.keys() for i in range(0, self.types[name]) ]
        self.draw_order = random.sample(cards, len(cards))
        self.discard_order = []
        self.completed_rounds = 0
    
    def __repr__(self):
        str_out = ("Deck with:\n  Draw pile: " + 
                str(len(self.draw_order)) + " cards\n  Discard pile: " + 
                str(len(self.discard_order)) + " cards\n")
        return str_out                  
        
    def draw(self):
        if len(self.draw_order) == 0:
            # Shuffle the discard pile if the draw pile is empty
            self.draw_order = random.sample(
                    self.discard_order, len(self.discard_order))
            self.discard_order = []
            self.completed_rounds += 1
        return self.draw_order.pop(0)
    
    def discard(self, c):
        if isinstance(c, list):
            for iCard in c:
                self.discard_order.append(iCard)
        else:
            self.discard_order.append(c)
        
    
class Player: 
    """Generic player class. Should be subtyped later for new strategies.
    Each player type must implement the following methods: 
        plant: takes an array of cards and plants them
    """
    def __init__(self, seat):
        self.hand = []
        self.field1 = []
        self.field2 = []
        self.points = 0
        self.point_discards = []
        self.name = "Generic" 
        self.seat = seat
        
    def __repr__(self):
        if len(self.field1) == 0:
            field1_name = "[Empty]"
        else:
            field1_name = str(self.field1[0]) + "(" + str(len(self.field1)) + ")" 
            
        if len(self.field2) == 0:
            field2_name = "[Empty]"
        else:
            field2_name = str(self.field2[0]) + "(" + str(len(self.field2)) + ")"
            
        return (self.name + " player (" + str(self.seat) + ").\nHand: " + 
                str(self.hand)
                    + "\nField 1: " + field1_name
                    + "\nField 2: " + field2_name)
        
    def plant_field(self, field, card, deck):
        if len(field) > 0 and card != field[0]:
            self.harvest_field(field, deck)
        field.append(card)

    def harvest_field(self, field, deck):
        """Get points return discarded cards."""
        nBeans = len(field)
        if nBeans == 0:
            return
        nPoints = sum(i <= nBeans for i in field[0].point_thresholds)
        self.points += nPoints
        deck.discard(field[0:(nBeans-nPoints)])
        self.point_discards.append(field[-nPoints:])
        field = []
        
        print("Harvest by " + str(self))

class AutarkyPlayer(Player):
    
    def __init__(self, seat):
        Player.__init__(self, seat)
        self.name = "Autarky" 
        
    def plant(self, cards, deck):
        """Plant one card, harvesting field 1 if neither field matches."""
        for iCard in cards:
            if len(self.field2) == 0 or iCard == self.field2[0]:
                self.plant_field(self.field2, iCard, deck)
            else:
                self.plant_field(self.field1, iCard, deck)
    
    def trade(self, cards): 
        """Trade with other players. Still working out what the mechanics of 
        this are 
        """
        return cards
            
class Game: 
    
    def __init__(self, players):
        self.deck = Deck()        
        self.players = players
        self.deal_game(len(self.players))
        
    def run(self):
        active_player = 0
        round_number = 1
        while not self.game_over():
            self.turn(self.players[active_player], round_number)
            active_player += 1
            if active_player >= len(self.players):
                active_player = 0
                round_number += 1
    
    def deal_game(self, nPlayers):
        """Initial game setup"""
        for iPlayer in range(0,nPlayers):
            for iCard in range(5):
                self.players[iPlayer].hand.append(self.deck.draw())
    
    def game_over(self):
        """The game is over after completing 3 times through the deck"""
        return len(self.deck.draw_order) == 0 and self.deck.completed_rounds >= 2
        
    def turn(self, player, round_number):
        """Have a player take a turn"""
        
        print("Turn " + str(round_number) + " for " + str(player))
        
        # Step 1: Plant fron hand
        player.plant([player.hand.pop()], self.deck)
        
        # Step 2a: Draw new cards 
        new_cards = [self.deck.draw(), self.deck.draw()]
        
        print("Drew cards:\n" + str(new_cards))
        
        # Step 2b: Trade cards
        cards = player.trade(new_cards)
        
        # Step 3: Plant new cards
        player.plant(cards, self.deck)
        
        # Step 4: Draw new cards
        for iCard in range(3):
            player.hand.append(self.deck.draw()) 
        
        print("Finished turn for " + str(player))
        print("================\n")
        
        return 0
       
if __name__ == "__main__":
    g = Game([AutarkyPlayer(i+1) for i in range(4)])
    g.run()