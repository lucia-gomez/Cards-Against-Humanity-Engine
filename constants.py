VALID = {'Yes': True, 'yes': True, 'Y': True, 'y': True, 'No': False, 'no': False, 'N': False, 'n': False}
NTH = {0: '', 1: 'first ', 2: 'second ', 3: 'third '}
DIVIDER = '=================================================='

LIMIT = 16
HEIGHT = 12
EMPTY_LINE = ' ' * LIMIT
MARGIN = ' ' * 2
CARD_GAP = ' ' * 2
CARD_WIDTH = (2 * len(MARGIN)) + LIMIT + 1 + len(CARD_GAP)

BOTTOM_SHADOW = '╚' + '═' * (LIMIT + 2 * len(MARGIN) - 1) + '╝'
SIDE_SHADOW = '║'
TOP_CORNER_SHADOW = '╗'

WHITE_FG = '\033[37m'
WHITE_BG = '\033[47m'
BLACK_FG = '\033[30m'
BLACK_BG = '\033[40m'
COVER_ART = '\033[1;31m'
RAINBOW = ['\033[1;31m', '\033[1;33m', '\033[1;92m', '\033[36m', '\033[34m', '\033[1;35m', '\033[1;95m']
