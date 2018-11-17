# Bohnanza Simulator

A simulator for [Bohnanza](http://riograndegames.com/Game/36-Bohnanza), a bean trading card game.

## Simulating Strategies
This code was designed to test out different strategies. The basic game components are available in `game.py`. 

A strategy is defined as a class that implements all necessary functions to run the game. Currently, these are: 
- `plant_from_hand`
- `plant_from_trade`
- `trade`

The trading functionality is still under development and subject to change. 

For an example of a strategy see `NaiveStrategy.py`, which shows that the average difference in points for 3 non-trading player decreases by starting position by less than 0.1 points per game on average. 
