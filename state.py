"""

Holds information about game state and mutates state.

"""

from typing import List, Tuple, Dict
from random import shuffle
from threading import Lock
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
    def __init__(self, is_wild, text='___'):
        Card.__init__(self, text)
        self.isWild = is_wild


class BlackCard(Card):
    def __init__(self, text, num_blanks):
        Card.__init__(self, text)
        self.numBlanks: int = num_blanks


class Player:
    def __init__(self, name, id):
        self.name: str = name
        self.hand: List[WhiteCard] = []
        self.score: int = 0
        self.id = id

    def pretty_print_hand(self):
        s = ''
        for i, card in enumerate(self.hand):
            s += str(i + 1) + ': ' + str(card) + '\n'
        return s

    def play_card(self, index: int) -> WhiteCard or None:
        card = self.hand[index - 1]
        self.hand[index - 1] = None
        if card is None:
            return None
        if card.isWild:
            raise Wildcard(index)
        return card

    def inc_score(self):
        self.score += 1

    def __str__(self):
        return self.name + ': ' + str(self.score)

    def __repr__(self):
        return self.name + ': ' + str(self.score)

    def __add__(self, other):
        return str(self) + other


class State:
    def __init__(self, white_cards, black_cards):
        self.players: List[Player] = []
        self.whiteCards: List[WhiteCard] = white_cards
        self.blackCards: List[BlackCard] = black_cards
        self.whiteDiscards = []
        self.blackDiscards = []
        self.submissions: Dict[Player, List[WhiteCard]] = {}
        self.round = 0
        self.pointsToWin = 3
        self.cardsPerHand = 7
        self.numWildcards = 30

        self.lock = Lock()

        self._add_wildcards()
        shuffle(self.whiteCards)
        shuffle(self.blackCards)

    def _add_wildcards(self):
        for _ in range(self.numWildcards):
            self.whiteCards.append(WhiteCard(True))

    def _draw_white_card(self) -> WhiteCard:
        with self.lock:
            if len(self.whiteCards) == 0:
                raise OutOfWhiteCards
            return self.whiteCards.pop()

    def _draw_black_card(self) -> BlackCard:
        if len(self.blackCards) == 0:
            raise OutOfBlackCards
        card = self.blackCards.pop()
        self.blackDiscards.append(card)
        return card

    def add_player(self, name: str, id: int):
        player = Player(name, id)
        [player.hand.append(self._draw_white_card()) for _ in range(self.cardsPerHand)]
        with self.lock:
            self.players.append(player)

    def pretty_player_names(self):
        if len(self.players) == 0:
            return ''
        s = self.players[0].name
        for p in self.players[1:]:
            s += ', ' + p.name
        return s

    def _split_players(self) -> Tuple[Player, List[Player]]:
        i = self.round % len(self.players)
        other_players = [player for j, player in enumerate(self.players) if i != j]
        return self.players[i], other_players

    def new_round(self) -> Tuple[Tuple[Player, List[Player]], BlackCard]:
        split_players = self._split_players()
        self.round += 1
        return split_players, self._draw_black_card()

    def submit(self, player: Player, index: int) -> bool:
        card = player.play_card(index)
        if not card:
            return False
        with self.lock:
            if player in self.submissions.keys():
                self.submissions[player].append(card)
            else:
                self.submissions[player] = [card]
        return True

    def submit_wildcard(self, player: Player, card_text: str, index: int):
        card = WhiteCard(False, card_text)
        player.hand[index-1] = card
        return self.submit(player, index)

    def draw_cards(self, player: Player):
        for i, card in enumerate(player.hand):
            if card is None:
                player.hand[i] = self._draw_white_card()

    def _pretty_print_submission(self, cards: List[WhiteCard]):
        c = str(cards[0])
        if len(cards) == 1:
            return c
        for card in cards[1:]:
            c += ', ' + str(card)
        return c

    def _pretty_print_all_submissions(self):
        s = ''
        for i, player in enumerate(self.submissions):
            c = self._pretty_print_submission(self.submissions[player])
            s += str(i+1) + ': ' + c + '\n'
        return s

    def print_submissions(self):
        keys = list(self.submissions.keys())
        shuffle(keys)
        self.submissions = {k: self.submissions[k] for k in keys}
        return self._pretty_print_all_submissions()

    def get_submissions(self) -> List[List[WhiteCard]]:
        keys = list(self.submissions.keys())
        shuffle(keys)
        self.submissions = {k: self.submissions[k] for k in keys}
        return list(self.submissions.values())

    def select_winner(self, index) -> Tuple[Player, str]:
        winner = list(self.submissions.keys())[index-1]
        cards = self.submissions[winner]
        for player in self.submissions:
            self.whiteDiscards.extend(self.submissions[player])
        self.submissions = {}
        winner.inc_score()
        return winner, cards
        # return winner, self._pretty_print_submission(cards)

    def get_scores(self):
        s = ''
        for player in self.players:
            s += player + '\n'
        return s

    def reset(self):
        for player in self.players:
            player.score = 0
