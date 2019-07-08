"""

Holds information about game state and mutates state.

"""

from typing import List, Tuple, Dict
from random import shuffle
from exceptions import *


class Card:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __add__(self, other):
        return str(self) + other


class WhiteCard(Card):
    def __init__(self, isWild, text='___'):
        Card.__init__(self, text)
        self.isWild = isWild


class BlackCard(Card):
    def __init__(self, text, numBlanks):
        Card.__init__(self, text)
        self.numBlanks: int = numBlanks


class Player:
    def __init__(self, name):
        self.name: str = name
        self.hand: List[WhiteCard] = []
        self.score: int = 0

    def prettyPrintHand(self):
        s = ''
        for i,card in enumerate(self.hand):
            s += str(i+1) + ': ' + str(card) + '\n'
        return s

    def playCard(self, index: int, newCard: WhiteCard) -> WhiteCard:
        card = self.hand[index-1]
        if card.isWild: raise Wildcard(index-1)
        self.hand[index-1] = newCard
        return card

    def incScore(self):
        self.score += 1

    def __str__(self):
        return self.name + ': ' + str(self.score)

    def __repr__(self):
        return self.name + ': ' + str(self.score)

    def __add__(self, other):
        return str(self) + other


class State:
    def __init__(self, whiteCards, blackCards):
        self.players: List[Player] = []
        self.whiteCards: List[WhiteCard] = whiteCards
        self.blackCards: List[BlackCard] = blackCards
        self.whiteDiscards = []
        self.blackDiscards = []
        self.submissions: Dict[Player, List[WhiteCard]] = {}
        self.round = 0
        self.pointsToWin = 1
        self.cardsPerHand = 7
        self.numWildcards = 200

        self._addWildcards()
        shuffle(self.whiteCards)
        shuffle(self.blackCards)


    def _addWildcards(self):
        for _ in range(self.numWildcards):
            self.whiteCards.append(WhiteCard(True))

    def _drawWhiteCard(self) -> WhiteCard:
        if len(self.whiteCards) == 0: raise OutOfWhiteCards
        return self.whiteCards.pop()

    def _drawBlackCard(self) -> BlackCard:
        if len(self.blackCards) == 0: raise OutOfBlackCards
        card = self.blackCards.pop()
        self.blackDiscards.append(card)
        return card

    def addPlayer(self, name: str):
        player = Player(name)
        [player.hand.append(self._drawWhiteCard()) for _ in range(self.cardsPerHand)]
        self.players.append(player)

    def _splitPlayers(self) -> Tuple[Player, List[Player]]:
        i = self.round % len(self.players)
        otherPlayers = [player for j, player in enumerate(self.players) if i != j]
        return (self.players[i], otherPlayers)

    def newRound(self) -> Tuple[Tuple[Player, List[Player]], BlackCard]:
        splitPlayers = self._splitPlayers()
        self.round += 1
        return splitPlayers, self._drawBlackCard()

    def submit(self, player: Player, cardNum: int):
        card = player.playCard(cardNum, self._drawWhiteCard())
        if player in self.submissions.keys():
            self.submissions[player].append(card)
        else:
            self.submissions[player] = [card]

    def _prettyPrintSubmission(self, cards: List[WhiteCard]):
        c = str(cards[0])
        if len(cards) == 1:
            return c
        for card in cards[1:]:
            c += ', ' + str(card)
        return c

    def _prettyPrintAllSubmissions(self):
        s = ''
        for i, player in enumerate(self.submissions):
            c = self._prettyPrintSubmission(self.submissions[player])
            s += str(i+1) + ': ' + c + '\n'
        return s

    def getSubmissions(self):
        keys = list(self.submissions.keys())
        shuffle(keys)
        self.submissions = {k: self.submissions[k] for k in keys}
        return self._prettyPrintAllSubmissions()

    def selectWinner(self, index) -> Tuple[Player, str]:
        winner = list(self.submissions.keys())[index-1]
        cards = self.submissions[winner]
        for player in self.submissions:
            self.whiteDiscards.extend(self.submissions[player])
        self.submissions = {}
        winner.incScore()
        return (winner, self._prettyPrintSubmission(cards))

    def getScores(self):
        s = ''
        for player in self.players:
            s += player + '\n'
        return s

    def reset(self):
        for player in self.players:
            player.score = 0
