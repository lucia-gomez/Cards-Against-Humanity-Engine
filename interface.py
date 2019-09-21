import colorama
from constants import COLORS, DIVIDER, RAINBOW, VALID

colorama.init(autoreset=True)


def printCoverArt(rainbow=False):
    # artLines = loadArt('art/coverArt.txt')
    with open('art/coverArt.txt', 'r') as file:
        lines = file.readlines()
    file.close()
    print()
    print(COLORS['COVER_ART'] + 'Welcome to...')
    for i, line in enumerate(lines):
        color = RAINBOW[i%len(RAINBOW)] if rainbow else COLORS['COVER_ART']
        print(color + line, end='')
    print('\n' + DIVIDER + '\n')


def print_username(name):
    print(COLORS['USERNAME'] + name, end='')


def player_joined(name: str, alreadyOnline: int = 0):
    if alreadyOnline == 0:
        print_username(name)
        print(' has joined the game')
    else:
        if len(name) > 0:
            print('Players already online: ', end='')
            print_username(name)
            print()
        else:
            print('No one is online yet')


def wildcard() -> str:
    return validateString('Enter text for your wildcard: ', 100)


def judge_pick(max_val: int, player_name: str):
    return validateInt('Judge ' + player_name + ', choose the winner: ',
                                      lambda x: 1 <= x <= max_val,
                                      'You must enter a number between 1 and ' +
                                      str(max_val) + '.')


def play_again(state):
    x = input('Do you want to play again? [Y/n]: ').strip()
    try:
        if x == '' or VALID[x]:
            reuse = input('Do you want to reuse the current game setup and players? [Y/n]: ').strip()
            print()
            return state if reuse == '' or VALID[reuse] else None
        exit(0)
    except:
        exit(0)


def validateInt(prompt: str, cond, errorMsg: str):
    while True:
        try:
            print(COLORS['PROMPT'] + prompt, end='')
            x = input()
            x = int(x)
            if cond(x):
                return x
            print(COLORS['ERROR'] + errorMsg)
            pass
        except KeyboardInterrupt:
            exit(0)
        except ValueError:
            print(COLORS['ERROR'] + 'Please enter a whole number.')


def validateString(prompt, maxLength):
    while True:
        print(COLORS['PROMPT'] + prompt, end='')
        x = input().strip()
        if x != '' and len(x) <= maxLength:
            return x
        if x == '':
            print(COLORS['ERROR'] + 'Value must be non-empty.')
        elif len(x) > maxLength:
            print(COLORS['ERROR'] + 'Value cannot be longer than ' +
                  str(maxLength) + ' characters. Your input was ' +
                  str(len(x)) + ' characters long.')