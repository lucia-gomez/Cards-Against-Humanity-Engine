"""

Holds information about game state and mutates state.

"""

from collections import defaultdict
from typing import List, Tuple, Dict
from random import shuffle
from threading import Lock
from exceptions import *
from constants import GameRules


class Card:
    """ Representation of a playing card.

    :param text: (str) The card text

    """
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __add__(self, other):
        return str(self) + other


class WhiteCard(Card):
    """ Representation of a white card in Cards Against Humanity,
        which are used to respond to questions. Includes wildcards,
        where the user provides custom text.

    :param is_wild: (bool) True if the card is a wildcard
    :text: (str) The card text

    """
    def __init__(self, is_wild, text=GameRules.WILDCARD_TEXT):
        Card.__init__(self, text)
        self.isWild = is_wild


class BlackCard(Card):
    """ Representation of a black card in Cards Against Humanity,
        which contain question or fill-in-the-blank statements.
        Black cards may have up to 3 blanks. 3 blanks means that a
        black card requires 3 white cards in response.

        :param text: (str) The card text
        :param num_blanks: (int) Number of white cards needed in response

    """
    def __init__(self, text, num_blanks):
        Card.__init__(self, text)
        self.numBlanks: int = num_blanks


class Player:
    """ Representation of a player, and the player's data.
        In addition to identifying information, a player has
        a hand of cards and a score to track their points.

    :param name: (str) The player's nickname or alias
    :param client_id: (int) The player's client ID

    """
    def __init__(self, name: str, client_id: int):
        self.name: str = name
        self.id: int = client_id
        self.hand: List[WhiteCard] = []
        self.score: int = 0

    # def pretty_print_hand(self):
    #     s = ''
    #     for i, card in enumerate(self.hand):
    #         s += str(i + 1) + ': ' + str(card) + '\n'
    #     return s

    def play_card(self, i: int) -> WhiteCard or None:
        """ Play the selected card from the player's hand

        :param i: (int) the card to play, starting at index 1
        :return: the (i-1)th card, or None if the card has already been played
        """
        card = self.hand[i - 1]
        self.hand[i - 1] = None
        if card is None:
            return None
        if card.isWild:
            raise Wildcard(i)
        return card

    def inc_score(self) -> int:
        self.score += 1
        return self.score

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
        self.submissions: Dict[Player, List[WhiteCard]] = defaultdict(list)
        self.round = 0

        self.pointsToWin = GameRules.POINTS_TO_WIN
        self.cardsPerHand = GameRules.CARDS_PER_HAND
        self.numWildcards = GameRules.NUM_WILDCARDS

        self.lock = Lock()

        self._add_wildcards()
        shuffle(self.whiteCards)
        shuffle(self.blackCards)

    def _add_wildcards(self):
        """
            Add wildcards into the deck of white cards
        """
        for _ in range(self.numWildcards):
            self.whiteCards.append(WhiteCard(True))

    def _draw_white_card(self) -> WhiteCard:
        """ Draw a white card from the deck

        :raises: OutOfWhiteCards if the deck is empty

        :return: a white card
        """
        with self.lock:
            if len(self.whiteCards) == 0:
                raise OutOfWhiteCards
            return self.whiteCards.pop()

    def _draw_black_card(self) -> BlackCard:
        """ Draw a black card from the deck

        :raises: OutOfBlackCards if the deck is empty

        :return: a black card
        """
        if len(self.blackCards) == 0:
            raise OutOfBlackCards
        card = self.blackCards.pop()
        self.blackDiscards.append(card)
        return card

    def add_player(self, name: str, client_id: int):
        """ Add a new player to the existing game,
            and draw their hand of white cards

        :param name: (str) The player's nickname
        :param client_id: (int) The player's server ID
        """
        player = Player(name, client_id)
        [player.hand.append(self._draw_white_card()) for _ in range(self.cardsPerHand)]
        with self.lock:
            self.players.append(player)

    def pretty_player_names(self):
        """ Pretty-print a list of current players

        :return: (str) A pretty-printed string containing the list of players
        """
        if len(self.players) == 0:
            return ''
        s = self.players[0].name
        for p in self.players[1:]:
            s += ', ' + p.name
        return s

    def _split_players(self) -> Tuple[Player, List[Player]]:
        """ Designate one player to be the judge, and the rest
            to be normal players for a round. Judges are selected in
            round robin order

        :return: (judge, other player list)
        """
        i = self.round % len(self.players)
        other_players = [player for j, player in enumerate(self.players) if i != j]
        return self.players[i], other_players

    def new_round(self) -> Tuple[Tuple[Player, List[Player]], BlackCard]:
        """ Setup a new round of the game: choose a new judge and draw a black card

        :return: ((judge, other player list), black card)
        """
        split_players = self._split_players()
        self.round += 1
        return split_players, self._draw_black_card()

    def submit(self, player: Player, index: int, is_wild=False) -> bool:
        """ Process a player's attempt to submit a white card for judgement.
            Attempt may be unsuccessful if the player has already played
            the desired card, which is possible for black cards that require
            multiple white cards

        :param player: The player trying to submit a card
        :param index: The number of the card the player selected, 1-based index
        :param is_wild: True if the card is a wildcard
        :return: True if the submission was successful
        """
        card = player.play_card(index)
        if not card:
            return False
        with self.lock:
            self.submissions[player].append(card)
            # recycle submitted white cards
            self.whiteDiscards.append(card if not is_wild else WhiteCard(True))
        return True

    def submit_wildcard(self, player: Player, card_text: str, index: int) -> bool:
        """ Allow a player to submit a wildcard, with the user-entered text.

        :param player: The player submitting a wildcard
        :param card_text: The custom white card text
        :param index: The number of the card the player selected, 1-based index
        :return: True if the submission was successful (should always be successful)
        """
        card = WhiteCard(False, card_text)
        player.hand[index-1] = card
        return self.submit(player, index, True)

    def draw_cards(self, player: Player):
        """ Draw new cards for the player, so that they have the correct number
            of cards in their hand. New cards will be added to the end of their hand.

        :param player: The player who is drawing cards
        """
        player.hand = list(filter(lambda x: x is not None, player.hand))
        for _ in range(GameRules.CARDS_PER_HAND - len(player.hand)):
            player.hand.append(self._draw_white_card())

    # def _pretty_print_submission(self, cards: List[WhiteCard]):
    #     c = str(cards[0])
    #     if len(cards) == 1:
    #         return c
    #     for card in cards[1:]:
    #         c += ', ' + str(card)
    #     return c
    #
    # def _pretty_print_all_submissions(self):
    #     s = ''
    #     for i, player in enumerate(self.submissions):
    #         c = self._pretty_print_submission(self.submissions[player])
    #         s += str(i+1) + ': ' + c + '\n'
    #     return s
    #
    # def print_submissions(self):
    #     keys = list(self.submissions.keys())
    #     shuffle(keys)
    #     self.submissions = {k: self.submissions[k] for k in keys}
    #     return self._pretty_print_all_submissions()

    def get_submissions(self) -> List[List[WhiteCard]]:
        """ Get the submissions for a round, in random order.
            Some black cards require more than one submitted white card,
            so a user's submission is a list of cards- a card set.

        :return: The submitted card sets for a round
        """
        keys = list(self.submissions.keys())
        shuffle(keys)
        self.submissions = {k: self.submissions[k] for k in keys}
        return list(self.submissions.values())

    def select_winner(self, index) -> Tuple[Player, str]:
        """ Process the judge's selection for a round: award the winner a point,
        and return the winner's name and the winning submission

        :param index: The number of the player selected, 1-based index
        :return: (winner's name, winning cards)
        """

        winner = list(self.submissions.keys())[index-1]
        cards = self.submissions[winner]
        # for player in self.submissions:
        #     self.whiteDiscards.extend(self.submissions[player])
        self.submissions = defaultdict(list)
        winner.inc_score()
        return winner, cards

    def is_game_over(self) -> bool:
        """ Check if anyone has won the game

        :return: True if a player has won
        """
        return any([p.score >= self.pointsToWin for p in self.players])

    def get_scores(self):
        """ Pretty-printed string of the scoreboard

        :return: the pretty-printed scoreboard
        """
        s = ''
        for player in self.players:
            s += player + '\n'
        return s

    def reset(self):
        """
            Reset the game
        """
        for player in self.players:
            player.score = 0
