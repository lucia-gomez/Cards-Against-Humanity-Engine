VALID = {'Yes': True, 'yes': True, 'Y': True, 'y': True, 'No': False, 'no': False, 'N': False, 'n': False}
NTH = {0: '', 1: 'first ', 2: 'second ', 3: 'third '}
DIVIDER = '=================================================='

### ASCII CARD GRAPHICS ###
# max number of characters per line on cards
LIMIT = 18
# height of a card, in number of lines
HEIGHT = 14
# an empty card line of text
EMPTY_LINE = ' ' * LIMIT
# horizontal padding between the edge of card and card text
MARGIN = ' ' * 2
# space between 2 cards in a hand
CARD_GAP = ' ' * 2
# total width of one card
CARD_WIDTH = (2 * len(MARGIN)) + LIMIT + 1 + len(CARD_GAP)
# space between 2 cards in a set, i.e. for 2-blank rounds
SET_GAP = lambda n: ' ' * 2 if n > 1 else ''
# total width of a set of cards, i.e. for 2-blank rounds
SET_WIDTH = lambda n: n * CARD_WIDTH + len(SET_GAP(n)) if n > 1 else CARD_WIDTH

# shadow on the bottom edge of cards
BOTTOM_SHADOW = '╚' + '═' * (LIMIT + 2 * len(MARGIN) - 1) + '╝'
# shadow for one line of a card side
SIDE_SHADOW = '║'
# shadow for top right-hand corner of cards
TOP_CORNER_SHADOW = '╗'

### ASCII COLORS ###
WHITE_FG = '\033[37m'
WHITE_BG = '\033[47m'
BLACK_FG = '\033[30m'
BLACK_BG = '\033[40m'
COLORS = {'COVER_ART': '\033[1;31m', 'ERROR': '\033[31m','PROMPT': '\033[92m',
          'USERNAME': '\033[36m', 'WIN': '\033[93m'}

RAINBOW = ['\033[1;31m', '\033[1;33m', '\033[1;92m', '\033[36m',
           '\033[34m', '\033[1;35m', '\033[1;95m']

### NETWORK CONSTANTS ###
BUFF_SIZE = 4096
CMD_SPLIT = '%%'
ENCODING = 'utf-8'
COMMANDS = {'ART': 0, 'PLAINTEXT': 1, 'NAME': 2, 'PLAYER_JOINED': 3, 'START_PLAYER_TURN': 4,
            'WILDCARD': 5, 'PLAYED': 6, 'PLAY_CARD': 7, 'PLAY_CARD_AGAIN': 8, 'JUDGE': 9,
            'WINNER': 10, 'WON_GAME': 11, 'BLACK_CARD': 14, 'KILL': 15}
