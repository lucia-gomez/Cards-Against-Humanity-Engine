import loader
import colorama
from state import Player, WhiteCard
from constants import COLORS, DIVIDER, RAINBOW

colorama.init(autoreset=True)


def printCoverArt(rainbow=False):
    artLines = loader.loadArt('coverArt.txt')
    print()
    print(COLORS['COVER_ART'] + 'Welcome to...')
    for i, line in enumerate(artLines):
        color = RAINBOW[i%len(RAINBOW)] if rainbow else COLORS['COVER_ART']
        print(color + line, end='')
    print('\n')
    print(DIVIDER)
    print()


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


def validateInt(prompt: str, cond, errorMsg: str):
    while True:
        try:
            print(COLORS['PROMPT'] + prompt, end='')
            x = int(input())
            if x == '^C':
                exit(0)
            if cond(x): return x
            print(COLORS['ERROR'] + errorMsg)
            pass
        except: print(COLORS['ERROR'] + 'Please enter a whole number.')


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