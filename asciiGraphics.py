import parser
import colorama
import shutil
from constants import *
from typing import List
from state import WhiteCard


def _format_card(text):
    lines = parser.get_card_lLines(text)
    pad = lambda line: MARGIN + line + MARGIN
    padded_lines = [pad(EMPTY_LINE)]

    for line in lines:
        assert(len(line) == LIMIT)
        padded_lines.append(pad(line))

    while len(padded_lines) < HEIGHT:
        padded_lines.append(pad(EMPTY_LINE))

    assert(len(padded_lines) == HEIGHT)
    return padded_lines


def _print_card_row(cards, n: int, bg, fg, labels=None):
    rows = [[] for _ in range(len(cards[0]))]
    [rows[j].append(line) for card in cards for j, line in enumerate(card)]

    colorama.init(autoreset=True)
    for i, row in enumerate(rows):
        for j, line in enumerate(row):
            print(bg + fg + line, end='')
            if i == 0:
                print(TOP_CORNER_SHADOW, end=CARD_GAP)
            else:
                print(SIDE_SHADOW, end=CARD_GAP)
            if j % n == (n - 1):
                print(end=SET_GAP(n))
        print()
    for i in range(len(cards)):
        if i % n == (n - 1):
            print(BOTTOM_SHADOW + CARD_GAP + SET_GAP(n), end='')
        else:
            print(BOTTOM_SHADOW + CARD_GAP, end='')
    print()

    print(' ' * int((SET_WIDTH(n) - len(SET_GAP(n)) - 2 * len(CARD_GAP)) / 2), end='')

    if labels is not None:
        if labels[0] + 1 < 10:
            print(end=' ')
        for i in labels:
            print(i + 1, end=(' ' * (int(SET_WIDTH(n)) - len(CARD_GAP))))
            if i + 1 < 10:
                print(end=' ')
    print('\n')


def _print_hand(cards: List[List[str]], is_white: bool):
    card_lines = [[_format_card(str(card)) for card in card_set] for card_set in cards]

    fg = BLACK_FG if is_white else WHITE_FG
    bg = WHITE_BG if is_white else BLACK_BG

    if len(cards) == 0:
        return
    n = len(cards[0])
    columns, lines = shutil.get_terminal_size()
    sets_per_line = int(columns / SET_WIDTH(n))

    for i in range(0, len(card_lines), sets_per_line):
        flat = [y for x in card_lines[i:i + sets_per_line] for y in x]
        _print_card_row(flat, n, bg, fg,
                        range(i, min(len(card_lines), i + sets_per_line)) if is_white else None)


def print_black_card(card: WhiteCard or str):
    _print_hand([[str(card)]], False)


def print_submissions(submissions: List[List[WhiteCard or str]]):
    _print_hand(submissions, True)


def print_player_hand(hand: List[WhiteCard or str]):
    _print_hand([[str(card)] for card in hand], True)


if __name__ == '__main__':
    # print_hand(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'])
    # print_hand([['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J'], ['K', 'L']])
    print_submissions([['A', 'B', 'C'], ['D', 'E', 'F']])
