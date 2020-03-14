from termcolor import colored
import shutil
from constants import *
from typing import List
from state import BlackCard, Card

def _pad(s):
    """ Given a line of text [s] less than [LIMIT] characters in length,
        pad it to [LIMIT] characters with whitespace

    :param s: (string) a single line of card text
    :return: (string) line of card text with length = LIMIT
    """
    return s + (' ' * (LIMIT - len(s)))


def _chunk(s):
    """ Split up text that is too long into two chunks,
        with the first chunk fitting on a card line.
        Requires len(s) > LIMIT

    :param s: (string), piece of text
    :return: (string, string): (good line of LIMIT chars or less, rest of line)
    """
    i = LIMIT
    # whitespace is a good breakpoint
    while i > 0 and s[i] != ' ':
        i -= 1
    # if no good breakpoint, insert a hyphen
    if i == 0:
        return s[:LIMIT-1] + '-', s[LIMIT-1:]
    return s[:i], s[i+1:]


def _get_card_lines(s):
    """ Convert card text to several card lines.

    :param s: (string) card text
    :return: (string list) lines of card text, with every line length = LIMIT
    """
    def _get_card_lines_helper(s, lines):
        """ Recursive helper function for get_card_lines

        :param s: (string) card text
        :param lines: (string list) lines of card text so far
        :return: (string list) lines of card text
        """
        if len(s) <= LIMIT:
            lines.append(_pad(s))
            return lines
        else:
            good, rest = _chunk(s)
            lines.append(_pad(good))
            return _get_card_lines_helper(rest, lines)
    return _get_card_lines_helper(s, [])


def _format_card(text):
    """ Given a card's text, format it into padded lines

    :param text: (string) card text
    :return: (string list) card lines, including empty lines to maintain card shape
    """
    lines = _get_card_lines(text)
    pad = lambda line: MARGIN + line + MARGIN  # add margin padding on both ends of line
    padded_lines = [pad(EMPTY_LINE)]

    # lines with text we have already processed
    for line in lines:
        assert(len(line) == LIMIT)
        padded_lines.append(pad(line))

    # add empty lines to maintain card shape
    while len(padded_lines) < HEIGHT:
        padded_lines.append(pad(EMPTY_LINE))

    assert(len(padded_lines) == HEIGHT)
    return padded_lines


def _card_row(cards: List[List[str]], set_size: int, bg: str, fg: str, labels=None):
    """ Convert a row of cards into a single string to print.
        Formats each piece of card text into a playing card,
        and groups card sets together

    :param cards: (string list) card lines for each card
    :param set_size: size of card sets
    :param bg: background color of card
    :param fg: foreground (text) color of card
    :param labels: numeric labels for each card set
    :return: (string) row of several colored cards to be printed
    """
    rows = [[] for _ in range(HEIGHT)]
    [rows[j].append(line) for card in cards for j, line in enumerate(card)]

    # result will be built by adding one line of a card at a time, for each card
    s = ''

    # add colored card lines, top corner and side shadows, and gaps between cards
    for row_num, row in enumerate(rows):
        for col_num, line in enumerate(row):
            shadow = SIDE_SHADOW if row_num != 0 else TOP_CORNER_SHADOW
            s += colored(bg + fg + line) + shadow + CARD_GAP
            if col_num % set_size == (set_size - 1):
                s += SET_GAP(set_size)
        s += '\n'

    # bottom line of each card: shadows and gaps
    for col_num in range(len(cards)):
        s += BOTTOM_SHADOW + CARD_GAP
        if col_num % set_size == (set_size - 1):
            s += SET_GAP(set_size)
    s += '\n'

    # add numeric labels underneath card sets
    s += (' ' * int((SET_WIDTH(set_size) - len(SET_GAP(set_size)) - 2 * len(CARD_GAP)) / 2))
    if labels is not None:
        if labels[0] + 1 < 10:
            s += ' '
        for i in labels:
            s += str(i + 1) + (' ' * (SET_WIDTH(set_size) - len(CARD_GAP)))
            if i + 1 < 10:
                s += ' '
    return s + '\n'


def _print_hand(cards: List[List[Card]], is_white: bool):
    """ Print a bunch of cards. Cards are arranged into sets, such as submissions
        for a black card with 2 blanks.

    Example: 4 2-sets [['A', 'B'], ['C, 'D'], ['E', 'F'], ['G', 'H']]
    Example: single card [['Test']]

    :param cards: (List[List[Card]])
    :param is_white: (bool) true if cards are white, false if black
    """
    card_lines = [[_format_card(str(card)) for card in card_set] for card_set in cards]

    fg = BLACK_FG if is_white else WHITE_FG
    bg = WHITE_BG if is_white else BLACK_BG

    if len(cards) == 0:
        return
    n = len(cards[0])
    columns, _ = shutil.get_terminal_size()
    sets_per_line = int(columns / SET_WIDTH(n))

    for i in range(0, len(card_lines), sets_per_line):
        flat = [y for x in card_lines[i:i + sets_per_line] for y in x]
        print(_card_row(flat, n, bg, fg,
                        range(i, min(len(card_lines), i + sets_per_line)) if is_white else None))


def print_black_card(card):
    """ Print one black card

    :param card: (Card) the black card to print
    """
    _print_hand([[card]], False)


def print_submissions(submissions):
    """ Print player submission sets for a black card,
        that the judge will choose from.

    :param submissions: (List[List[Card]]) the submitted card sets
    """
    _print_hand(submissions, True)


def print_player_hand(hand):
    """ Print the white cards in a player's hand

    :param hand: (List[Card]) the cards in a player's hand
    """
    _print_hand([[card] for card in hand], True)


def _diagnostic():
    # normal hand
    print_submissions([['A'], ['B'], ['C'], ['D'], ['E']])
    # 2-sets
    print_submissions([['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J'], ['L', 'M']])
    # 3-sets
    print_submissions([['A', 'B', 'C'], ['D', 'E', 'F']])
    # black card
    print_black_card(BlackCard("What am I?", 1))
    # multi-line
    print_player_hand(['ABCDEFGHIJKLMNOPQRSTUVWXYZ'])


if __name__ == '__main__':
    _diagnostic()
