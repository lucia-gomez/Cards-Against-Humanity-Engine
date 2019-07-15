from parser import getCardLines
from constants import *
from state import Card, WhiteCard, BlackCard
from typing import List
import colorama
import shutil


def _formatCard(text):
    lines = getCardLines(text)
    pad = lambda line: MARGIN + line + MARGIN
    paddedLines = [pad(EMPTY_LINE)]

    for line in lines:
        assert(len(line) == LIMIT)
        paddedLines.append(pad(line))

    while len(paddedLines) < HEIGHT:
        paddedLines.append(pad(EMPTY_LINE))

    assert(len(paddedLines) == HEIGHT)
    return paddedLines


def _printCardRow(cards, bg, fg, labels=None):
    rows = [[] for _ in range(len(cards[0]))]
    [rows[j].append(line) for card in cards for j, line in enumerate(card)]

    colorama.init(autoreset=True)
    for i, row in enumerate(rows):
        for line in row:
            print(bg + fg + line, end='')
            if i == 0:
                print(TOP_CORNER_SHADOW, end=CARD_GAP)
            else:
                print(SIDE_SHADOW, end=CARD_GAP)
        print()
    print(len(cards)*(BOTTOM_SHADOW+CARD_GAP))

    print(' ' * int((CARD_WIDTH - len(CARD_GAP) - 2) / 2), end='')
    if labels is not None:
        if labels[0] + 1 < 10:
            print(end=' ')
        for i in range(len(cards)):
            print(labels[i] + 1, end=' ' * (CARD_WIDTH - 2))
            if labels[i] + 1 < 10:
                print(end=' ')
    print('\n')


def _printHand(cards: List[Card], isWhite):
    cardLines = [_formatCard(card) for card in cards]
    # ensure all cards have the same dimensions
    height = len(cardLines[0])
    width = len(cardLines[0][0])
    assert (all([len(card) == height and len(card[0]) == width for card in cardLines]))

    fg = BLACK_FG if isWhite else WHITE_FG
    bg = WHITE_BG if isWhite else BLACK_BG

    columns, lines = shutil.get_terminal_size()
    cardsPerLine = int(columns / CARD_WIDTH)
    for i in range(0, len(cardLines), cardsPerLine):
        _printCardRow(cardLines[i:i+cardsPerLine], bg, fg, range(i, i+cardsPerLine) if isWhite else None)


def printWhiteHandMulti(cards: List[WhiteCard]):
    pass


def printWhiteHand(cards: List[WhiteCard]):
    _printHand(cards, True)


def printBlackCard(card: BlackCard):
    _printHand([card], False)


if __name__ == '__main__':
    printWhiteHand(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'])
    # printWhiteHand([['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J'], ['K', 'L']])
