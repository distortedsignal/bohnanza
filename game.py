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
    types = {'garden':[2, 2, 3], 'red': [2, 3, 4, 5], 
             'black-eyed': [2, 4, 5, 6], 'soy': [2, 4, 6, 7], 
             'green': [3, 5, 6, 7], 'stink': [3, 5, 7, 8], 
             'chili': [3, 6, 8, 9], 'blue': [4, 6, 8, 10]}
    
    def __init__(self,name):
        self.name = name
        self.point_thresholds = self.types[self.name]
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, card2):
        return self.name == card2.name
    
class Deck:  
    
    types = {'garden': 6, 'red': 8, 'black-eyed': 10, 'soy': 12, 
             'green': 14, 'stink': 16, 'chili': 18, 'blue': 20}
    
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
        
    def draw(self, nCards):
        """Get nCards from the deck
        If there are no cards left, you get only as many as are available
        """
        out = []
        for iC in range(nCards):
            out.append(self.draw_single())
        return out
    
    def draw_single(self):
        """Get a single card from the deeck"""
        if len(self.draw_order) == 0:
            # Shuffle the discard pile if the draw pile is empty
            self.draw_order = random.sample(
                    self.discard_order, len(self.discard_order))
            self.discard_order = []
            self.completed_rounds += 1
        if len(self.draw_order) == 0:
            return []
        else: 
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
                    + "\nField 2: " + names[1] + "\n")
        
    def plant_from_hand(self, game_state):
        """Get strategy's choice and execute"""
        if len(self.hand) == 0:
            return
        field_to_plant, cards = self.strategy.plant_from_hand(self)
        for (iField, iCard) in zip(field_to_plant, cards):
            self.plant_field(iField, iCard, game_state)
            self.hand.pop(0)
        
    def plant_from_draw(self, cards, game_state):
        """Get strategy's choice and execute"""
        field_to_plant, cards = \
            self.strategy.plant_from_trade(self, cards)
        for (iField, iCard) in zip(field_to_plant, cards):
            self.plant_field(iField, iCard, game_state)
     
    def plant_field(self, field_num, card, game_state):
        """Put card down on field, harvest if neccessary"""
        if len(self.fields[field_num]) > 0 and \
              card != self.fields[field_num][0]:
            self.harvest_field(field_num, game_state)
        self.fields[field_num].append(card)
    
    def harvest_field(self, field_num, game_state):
        """Get points, discard cards to correct place"""
        nBeans = len(self.fields[field_num])
        if nBeans == 0:
            return []
        nPoints = sum([i <= nBeans for i in self.fields[field_num][0].point_thresholds])
        self.points += nPoints
        
        for_discard = self.fields[field_num][0:(nBeans-nPoints)]
        for_points = self.fields[field_num][(nBeans-nPoints):]
        if len(for_discard) + len(for_points) != nBeans:
            print('error')
            raise AssertionError("Improper harvest.")
                
        # Handle cards from field
        game_state._deck.discard(for_discard)
        self.point_discards.extend(for_points)
        
        # Empty the field
        self.fields[field_num] = []
      
class Game: 
    
    def __init__(self, player_strats):
        self._deck = Deck()
        self._players = [Player(i, player_strats[i]) for i in range(len(player_strats))]
        self.deal_game(len(self._players))
        
    def __repr__(self):
        return "Bohnanza game with \n" + str(self._players) + " players."
        
    def run(self):
        active_player = 0
        round_number = 1
        empty_deck = False
        while not (self.game_over() or empty_deck):
            empty_deck = self.turn(active_player)
            active_player += 1

            if active_player >= len(self._players):
                active_player = 0
                round_number += 1
        points = [p.points for p in self._players]
        return points
    
#        print("GAME OVER\nPlayer points: " + \
#              str([p.points for p in self._players]))
        
    def deal_game(self, nPlayers):
        """Initial game setup"""
        for iPlayer in range(0,nPlayers):
            self._players[iPlayer].hand.extend(self._deck.draw(5))
    
    def game_over(self):
        """The game is over after completing 3 times through the deck"""
        return len(self._deck.draw_order) == 0 and \
            self._deck.completed_rounds >= 2
        
    def turn(self, player_num):
        """Have a player take a turn"""
        
        self.gamestate_is_valid()

        # Step 1: Plant fron hand
        self._players[player_num].plant_from_hand(self)
        
        self.gamestate_is_valid()

        # Step 2: Draw new cards & trade
        faceup_cards = self._deck.draw(2)
        if (len(faceup_cards) != 2) or any([not card for card in faceup_cards]):
            self._deck.discard(faceup_cards)
            return 1
        # trade_spec = self._strategy[player_num].trade(faceup_cards)
        # self.execute_trade(trade_spec)
        self.gamestate_is_valid(faceup_cards)
        
        # Step 3: Plant new cards
        self._players[player_num].plant_from_draw(faceup_cards, self)
        
        self.gamestate_is_valid()
        
        # Step 4: Draw new cards
        new_cards = self._deck.draw(3)
        if (len(new_cards) != 3) or any([not card for card in new_cards]):
            self._deck.discard(new_cards)
            return 1
        self._players[player_num].hand.extend(new_cards) 

        self.gamestate_is_valid()

    def gamestate_is_valid(self, addl_cards=[], throw_exception=False):
        """
        If !throw_exception, returns a boolean of if the game state is valid
        If throw_exception, throws an exception if the game state is not valid
        """
        original_types = Deck.types
        current_cards = defaultdict(int)

        for card in self._deck.draw_order:
            current_cards[card.name] += 1
        for card in self._deck.discard_order:
            current_cards[card.name] += 1
        for card in addl_cards: 
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
    g = Game([AutarkyStrategy(i) for i in range(nPlayers)])
    return g.run()

if __name__ == "__main__":
    points = []
    for iRun in range(5000):
        points.append(simulate(3))
    
    avg = [sum([p[i] for p in points])/len(points) for i in range(len(points[0]))]
    print(avg)
    