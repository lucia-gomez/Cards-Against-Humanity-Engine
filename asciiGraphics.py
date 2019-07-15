from parser import getCardLines
from constants import *
import colorama
import shutil


def formatCard(text):
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


def printCard(text, fg, bg):
    cardLines = formatCard(text)

    colorama.init(autoreset=True)
    for i, line in enumerate(cardLines):
        print(bg + fg + line, end='')
        if i == 0:
            print(TOP_CORNER_SHADOW)
        else: print(SIDE_SHADOW)
    print(BOTTOM_SHADOW)


def printCardRow(cards):
    rows = [[] for _ in range(len(cards[0]))]
    [rows[j].append(line) for card in cards for j, line in enumerate(card)]

    colorama.init(autoreset=True)
    for i, row in enumerate(rows):
        for line in row:
            print(WHITE_BG + BLACK_FG + line, end='')
            if i == 0:
                print(TOP_CORNER_SHADOW, end=CARD_GAP)
            else:
                print(SIDE_SHADOW, end=CARD_GAP)
        print()
    print(len(cards)*(BOTTOM_SHADOW+CARD_GAP))
    print()


def printHand(texts, isWhite):
    cards = [formatCard(text) for text in texts]
    # ensure all cards have the same dimensions
    cardHeight = len(cards[0])
    cardWidth = len(cards[0][0])
    assert (all([len(card) == cardHeight and len(card[0]) == cardWidth for card in cards]))

    columns, lines = shutil.get_terminal_size()
    cardWidth = 2*len(MARGIN) + LIMIT + len(CARD_GAP)
    cardsPerLine = int(columns / cardWidth)

    for i in range(0, len(cards), cardsPerLine):
        printCardRow(cards[i:i+cardsPerLine])
