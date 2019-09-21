VALID = {'Yes': True, 'yes': True, 'Y': True, 'y': True, 'No': False, 'no': False, 'N': False, 'n': False}
NTH = {0: '', 1: 'first ', 2: 'second ', 3: 'third '}
DIVIDER = '=================================================='

### ASCII CARD GRAPHICS ###
LIMIT = 18
HEIGHT = 14
EMPTY_LINE = ' ' * LIMIT
MARGIN = ' ' * 2
CARD_GAP = ' ' * 2
SET_GAP = lambda n: ' ' * 2 if n > 1 else ''
CARD_WIDTH = (2 * len(MARGIN)) + LIMIT + 1 + len(CARD_GAP)
SET_WIDTH = lambda n: n * CARD_WIDTH + len(SET_GAP(n)) if n > 1 else CARD_WIDTH


BOTTOM_SHADOW = '╚' + '═' * (LIMIT + 2 * len(MARGIN) - 1) + '╝'
SIDE_SHADOW = '║'
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
