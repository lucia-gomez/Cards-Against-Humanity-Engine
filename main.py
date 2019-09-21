from state import *
from exceptions import *
from constants import DIVIDER, NTH, RAINBOW, COLORS
from asciiGraphics import print_player_hand, print_black_card, print_submissions
import colorama
import interface
import loader


global game_state


def load_players():
    num_players = interface.validateInt('Enter number of players: ',
                                        (lambda x: 2 < x <= 20),
                                        'Number of players must be between 2 and 20.')
    for i in range(num_players):
        game_state.add_player(interface.validateString('Enter Player ' +
                              str(i + 1) +
                              '\'s name: ', 30).upper(), i)


def player_turn(blanks: int, player: Player):
    max_val = game_state.cardsPerHand
    print_player_hand(player.hand)
    offset = 1 if blanks > 1 else 0
    for i in range(blanks):
        try:
            while True:
                selection = interface.validateInt('Select your ' + NTH[i + offset] +
                                                  'card: ', (lambda x: 1 <= x <= max_val),
                                                  'You must enter a number between 1 and '
                                                  + str(max_val) + '.')
                if game_state.submit(player, selection):
                    break
                print(COLORS['ERROR'] + 'You already played this card! '
                                        'Choose another card to play.')
        except Wildcard as e:
            text = interface.wildcard()
            game_state.submit_wildcard(player, text, e.index)
    game_state.draw_cards(player)


def judge_turn(player: Player):
    # max_val = len(state.submissions)
    # selection = interface.validateInt('Judge ' + player.name + ', choose the winner: ',
    #                                   lambda x: 1 <= x <= max_val,
    #                                   'You must enter a number between 1 and ' +
    #                                   str(max_val) + '.')
    selection = interface.judge_pick(len(game_state.submissions), player.name)
    return game_state.select_winner(selection)


def play_round():
    (judge, players), black_card = game_state.new_round()
    for player in players:
        print(DIVIDER + '\n')
        print(judge.name + ' is judging: ')
        print_black_card(black_card)
        print(player.name + '\'s hand:\n')
        player_turn(black_card.numBlanks, player)
        print()
    print(DIVIDER + '\n')
    print(str(black_card) + '\n')
    print_submissions(game_state.get_submissions())
    winner, winning_cards = judge_turn(judge)
    print()
    print(winner.name + ' won with ' + str(winning_cards) + '!\n')
    print(game_state.get_scores())
    if game_state.is_game_over():
        raise GameOver(winner)


def init(state=None):
    global game_state
    if state is None:
        game_state = State(loader.loadWhiteCards('white_cards.csv'),
                           loader.loadBlackCards('black_cards.csv'))
        load_players()
    while True:
        try:
            play_round()
        except GameOver as e:
            print(e.player.name + ' WON!\n')
            break
    init(interface.play_again(game_state))


if __name__ == '__main__':
    colorama.init(autoreset=True)
    interface.printCoverArt()
    init()
