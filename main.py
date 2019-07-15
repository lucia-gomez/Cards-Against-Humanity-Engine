from loader import *
from state import *
from exceptions import *
import colorama
from colorama import Fore, Back, Style

valid = {'Yes': True, 'yes': True, 'Y': True, 'y': True, 'No': False, 'no': False, 'N': False, 'n': False}
nth = {0: '', 1: 'first ', 2: 'second ', 3: 'third '}
divider = '======================================'


def validateInt(prompt: str, cond, errorMsg: str):
    while True:
        try:
            x = int(input(prompt))
            if cond(x): return x
            print(errorMsg)
            pass
        except: print('Please enter a whole number.')


def validateString(prompt, maxLength):
    while True:
        x = input(prompt).strip()
        if x != '' and len(x) <= maxLength:
            return x
        if x == '':
            print('Value must be non-empty.')
        elif len(x) > maxLength:
            print('Value cannot be longer than ' + str(maxLength) +
                  ' characters. Your input was ' + str(len(x)) + ' characters long.')


def loadPlayers(state: State):
    numPlayers = validateInt('Enter number of players: ', (lambda x: 2<x<=20),
                             'Number of players must be between 2 and 20.')
    for i in range(numPlayers):
        state.addPlayer(validateString('Enter Player '+str(i+1)+'\'s name: ', 30).upper())


def wildcard(player: Player, index: int, state: State):
    x = validateString('Enter text for your wildcard: ', 100)
    card = WhiteCard(False, x)
    player.hand[index] = card


def playerTurn(blanks: int, player: Player, state: State):
    max = state.cardsPerHand
    print(player.prettyPrintHand())
    offset = 1 if blanks > 1 else 0
    selections = []
    for i in range(blanks):
        x = validateInt('Select your ' + nth[i + offset] + 'card: ', (lambda x: 1<=x<=max),
                    'You must enter a number between 1 and ' + str(max) + '.')
        while x in selections:
            print('You already played this card! Choose another one to play.')
            x = validateInt('Select your ' + nth[i + offset] + 'card: ', (lambda x: 1 <= x <= max),
                            'You must enter a number between 1 and ' + str(max) + '.')
        selections.append(x)
        try:
            state.submit(player, x)
        except Wildcard as e:
            wildcard(player, e.index, state)
            state.submit(player, x)


def judgeTurn(player: Player, state: State):
    max = len(state.submissions)
    x = validateInt('Judge ' + player.name + ', choose the winner: ', lambda x: 1<=x<=max,
                    'You must enter a number between 1 and ' + str(max) + '.')
    return state.selectWinner(x)


def playRound(state: State):
    (judge, players), blackCard = state.newRound()
    for player in players:
        print(divider + '\n')
        print(judge.name + ' is judging: ')
        print(blackCard + '\n')
        print(player.name + '\'s hand:\n')
        playerTurn(blackCard.numBlanks, player, state)
        print()
    print(divider + '\n')
    print(str(blackCard) + '\n')
    print(state.getSubmissions())
    winner, winningCards = judgeTurn(judge, state)
    print()
    print(winner.name + ' won with ' + str(winningCards) + '!\n')
    print(state.getScores())
    if winner.score >= state.pointsToWin:
        raise GameOver(winner)


def playAgain(state: State):
    x = input('Do you want to play again? [Y/n]: ').strip()
    try:
        if x == '' or valid[x]:
            reuse = input('Do you want to reuse the current game setup and players? [Y/n]: ').strip()
            print()
            return (state if reuse == '' or valid[reuse] else None)
        exit(0)
    except:
        exit(0)


def init(state=None):
    if state is None:
        state = State(loadWhiteCards('white_cards.csv'), loadBlackCards('black_cards.csv'))
        loadPlayers(state)
    while True:
        try:
            playRound(state)
        except GameOver as e:
            print(e.player.name + ' WON!\n')
            break
    state.reset()
    init(playAgain(state))


if __name__ == '__main__':
    init()