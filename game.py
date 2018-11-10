"""
An implementation of Bohnanza

@author: David Kelley, 2018
"""

import random 
from collections import defaultdict

class Card: 
    """Card Object
    Name  and point thresholds are the only properties. The point thresholds 
    are organized the way they are on the card - to get 1 point, you need th
    number of cards listed first in the point_thresholds, 2 for the 2nd, ... 
    """
    types = {'black':[2, 2, 3], 'pinto': [3, 6, 8, 12], 'chili': [3, 5, 5, 8]}
    
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
    def __init__(self, seat, strat):
        self.hand = []
        self.fields = [[], []]
        self.points = 0
        self.point_discards = []
        self.seat = seat
        self.strategy = strat
        
    def __repr__(self):
        names = []
        for iField in range(2):    
            if len(self.fields[iField]) == 0:
                names.append("[Empty]")
            else:
                names.append(str(self.fields[iField][0]) + \
                                 "(" + str(len(self.fields[iField])) + ")")
                
        return ("Player " + str(self.seat+1) + ".\nHand: " + 
                str(self.hand)
                    + "\nField 1: " + names[0]
                    + "\nField 2: " + names[1])
        
    def plant_from_hand(self, game_state):
        field_to_plant, cards = self.strategy.plant()
        self.plant_field(field_to_plant, cards, game_state)
    
    def plant_from_trade(self, game_state, cards):
        field_to_plant, cards = self.strategy.plant_from_trade()
        self.plant_field(field_to_plant, cards, game_state)
        
    def plant_field(self, field_num, card, game_state):
        if len(self.fields[field_num]) > 0 and \
              card != self.fields[field_num][0]:
            discards = self.harvest_field(field_num)
        self.fields[field_num].append(card)
        return discards
    
    def harvest_field(self, field_num, game_state):
        """Get points return discarded cards."""
        nBeans = len(self.fields[field_num])
        if nBeans == 0:
            return []
        nPoints = sum(i <= nBeans for i in \
                      self.fields[field_num][0].point_thresholds)
        self.points += nPoints
        game_state._deck.discard(self.fields[field_num][0:(nBeans-nPoints)])
        self.point_discards.append(self.fields[field_num][-nPoints:])
        self.fields[field_num] = []
        
class Strategy: 
    
    def __init__(self, seat):
        self.name = "Generic" 
        
    def __repr__(self): 
        return self.name + " player."
        
    def plant_from_hand(self, cards, player):
        """Return a list of which field to put cards in for the given player
        """
        pass
    
    def plant_from_trade(self, cards, player):
        """Return a list of which field to put cards in for the given player
        """
        pass
    
    def trade(self, cards):
        """Trade with other players. Still working out what the mechanics of 
        this are 
        """
        pass
    
class AutarkyStrategy(Strategy):
    """Example class for player strategy. This player does not trade.
    
    To be expanded later with trading. 
    """
    
    def __init__(self, seat):
        self.name = "Autarky" 
        
    def plant_from_hand(self, player):
        """Plant one card, harvesting field 1 if neither field matches."""
        if len(player.hand) == 0: 
            plants = []
            field_to_plant = []
            return [field_to_plant, plants]
        
        if len(player.hand) == 1:
            plants = player.hand[0]
        elif player.hand[0] == player.hand[1]:
            plants = player.hand[0:1]
        elif (player.hand[0] == player.fields[0] and \
                  player.hand[1] == player.fields[1]) or \
                  (player.hand[0] == player.fields[1] and \
                  player.hand[1] == player.fields[0]):
            plants = player.hand[0:1]
            if plants[0] == player.fields[0]: 
                fields_to_plant = [0]
                         
        if len(self.field2) == 0 or player.hand[0] == self.field2[0]:
            fields_to_plant = 2
        else:
            fields_to_plant = 1
            
        return [fields_to_plant, plants]

    def plant_from_trade(self, player, cards): 
        pass

    def trade(self, player, game, cards): 
        pass
            
class Game: 
    
    def __init__(self, player_strats):
        self._deck = Deck()
        self._players = [Player(i, player_strats[i]) for i in range(len(player_strats))]
        self.deal_game(len(self._players))
        
    def __repr__(self):
        return "Bohnanza game with " + str(self._players) + " players."
        
    def run(self):
        active_player = 0
        round_number = 1
        while not self.game_over():
            self.turn(active_player)
            active_player += 1

            if active_player >= len(self._players):
                active_player = 0
                round_number += 1

        print("GAME OVER\nPlayer points: " + \
              str([p.points for p in self._players]))
        
    def deal_game(self, nPlayers):
        """Initial game setup"""
        for iPlayer in range(0,nPlayers):
            for iCard in range(5):
                self._players[iPlayer].hand.append(self._deck.draw())
    
    def game_over(self):
        """The game is over after completing 3 times through the deck"""
        return len(self._deck.draw_order) == 0 and \
            self._deck.completed_rounds >= 2
        
    def turn(self, player_num):
        """Have a player take a turn"""
        
        #print("Turn " + str(round_number) + " for " + str(player))
        
        # Step 1: Plant fron hand
        self._player[player_num].plant(self)
        
        
#        field_to_plant = self._strategy[player_num].plant_from_hand(
#                self._players[player_num])
#        discards = self._players[player_num].plant_field(field_to_plant, 
#                     self._players[player_num].hand.pop())
#        self._deck.discard(discards)
#        
        # Step 2a: Draw new cards & trade
        new_cards = [self.deck.draw(), self.deck.draw()]
        # trade_spec = self._strategy[player_num].trade(new_cards)
        # TODO: Handle trading between players
        
        # Step 3: Plant new cards
        self._players[player_num].plant_from_draw(new_cards, self)
        
        # Step 4: Draw new cards
        for iCard in range(3):
            self._players[player_num].hand.append(self.deck.draw()) 
        
#        print("Finished turn for " + str(player))
#        print("================\n")
        
        return 0

    def gamestate_is_valid(self, throw_exception=False):
        """
        If throw_exception is false, returns a boolean of if the game state is valid
        If throw_exception is true, throws an exception if the game state is not valid
        """
        original_types = Deck.types
        current_cards = defaultdict(int)

        for card in self._deck.draw_order:
            current_cards[card.name] += 1
        for card in self._deck.discard_order:
            current_cards[card.name] += 1

        for player in self._players:
            for card in player.hand:
                current_cards[card.name] += 1
            for card in player.point_discards:
                current_cards[card.name] += 1
            for field in player.fields:
                for card in field:
                    current_cards[card.name] += 1

        for key in original_types:
            if original_types[key] != current_cards[key]:
                if not throw_exception:
                    return False
                raise AssertionError("not all cards are present")
        return True

       
def simulate(nPlayers):
    g = Game([AutarkyStrategy(i+1) for i in range(nPlayers)])
    g.run()
    return g

if __name__ == "__main__":
    g = simulate(3)
    
#    total_cards = (len(g.deck.draw_order) + 
#                   len(g.deck.discard_order) + 
#                   sum([len(p.hand) for p in g.players]))
#    
#    print("Total cards: " + str(total_cards))