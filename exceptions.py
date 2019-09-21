"""
Custom exceptions raised during gameplay
"""

'''
Raised when there are no more white cards in the deck.
'''
class OutOfWhiteCards(Exception):
    pass

''' 
Raised when there are no more black cards in the deck.
'''
class OutOfBlackCards(Exception):
    pass

''' 
Raised when a player has won the game.
'''
class GameOver(Exception):
    def __init__(self, player):
        self.player = player

''' 
Raised when a player plays a wildcard that needs to be filled in.
'''
class Wildcard(Exception):
    def __init__(self, index):
        self.index = index

'''
Raised when a player disconnects from the game server/
'''
class PlayerDisconnected(Exception):
    def __init__(self, player):
        self.player = player
