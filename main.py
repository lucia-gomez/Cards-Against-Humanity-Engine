from state import *
from exceptions import *
from loader import loadWhiteCards, loadBlackCards
from constants import DIVIDER, NTH, VALID, COLORS
from asciiGraphics import print_player_hand, print_black_card, print_submissions
import colorama
import interface


def load_players(state: State):
    num_players = interface.validateInt('Enter number of players: ',
                                        (lambda x: 2 < x <= 20),
                                        'Number of players must be between 2 and 20.')
    for i in range(num_players):
        state.add_player(interface.validateString('Enter Player ' +
                                                 str(i + 1) +
                                                 '\'s name: ', 30).upper(), i)


def player_turn(blanks: int, player: Player, state: State):
    max_val = state.cardsPerHand
    print_player_hand(player.hand)
    offset = 1 if blanks > 1 else 0
    for i in range(blanks):
        try:
            while True:
                selection = interface.validateInt('Select your ' + NTH[i + offset] +
                                                  'card: ', (lambda x: 1 <= x <= max_val),
                                                  'You must enter a number between 1 and '
                                                  + str(max_val) + '.')
                if state.submit(player, selection):
                    break
                print(COLORS['ERROR'] + 'You already played this card! '
                                        'Choose another card to play.')
        except Wildcard as e:
            text = interface.wildcard()
            state.submit_wildcard(player, text, e.index)
    state.draw_cards(player)


def judge_turn(player: Player, state: State):
    # max_val = len(state.submissions)
    # selection = interface.validateInt('Judge ' + player.name + ', choose the winner: ',
    #                                   lambda x: 1 <= x <= max_val,
    #                                   'You must enter a number between 1 and ' +
    #                                   str(max_val) + '.')
    selection = interface.judge_pick(len(state.submissions), player.name)
    return state.select_winner(selection)


def play_round(state: State):
    (judge, players), black_card = state.new_round()
    for player in players:
        print(DIVIDER + '\n')
        print(judge.name + ' is judging: ')
        print_black_card(black_card)
        print(player.name + '\'s hand:\n')
        player_turn(black_card.numBlanks, player, state)
        print()
    print(DIVIDER + '\n')
    print(str(black_card) + '\n')
    print_submissions(state.get_submissions())
    winner, winning_cards = judge_turn(judge, state)
    print()
    print(winner.name + ' won with ' + str(winning_cards) + '!\n')
    print(state.get_scores())
    if winner.score >= state.pointsToWin:
        raise GameOver(winner)


def play_again(state: State):
    x = input('Do you want to play again? [Y/n]: ').strip()
    try:
        if x == '' or VALID[x]:
            reuse = input('Do you want to reuse the current game setup and players? [Y/n]: ').strip()
            print()
            return state if reuse == '' or VALID[reuse] else None
        exit(0)
    except:
        exit(0)


def init(state=None):
    if state is None:
        state = State(loadWhiteCards('white_cards.csv'), loadBlackCards('black_cards.csv'))
        load_players(state)
    while True:
        try:
            play_round(state)
        except GameOver as e:
            print(e.player.name + ' WON!\n')
            break
    state.reset()
    init(play_again(state))


if __name__ == '__main__':
    colorama.init(autoreset=True)
    interface.printCoverArt()
    init()
