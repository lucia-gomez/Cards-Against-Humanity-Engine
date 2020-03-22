from state import *
from exceptions import *
from constants import DIVIDER, NTH, COLORS
import asciiGraphics
import colorama
import interface
import loader


global game_state


def load_players():
    """ Prompt the user to set up the game players. There must be between
        2 and 20 players, and each player may have a username of
        at most 30 characters.
    """
    num_players = interface.validateInt('Enter number of players: ',
                                        (lambda x: 2 < x <= 20),
                                        'Number of players must be between 2 and 20.')
    for i in range(num_players):
        name = interface.validateString('Enter Player ' + str(i + 1) + '\'s name: ', 30).upper()
        game_state.add_player(name, i)


def submit_valid_card(player: Player, i: int):
    """ Prompt the user to select a card until they make a valid selection,
        meaning a valid number card that they have not already played in this round

    :param player: the player trying to submit a card
    :param i: the order of the card being asked for (1st, 2nd, 3rd)
    """
    max_val = game_state.cardsPerHand
    while True:
        selection = interface.validateInt('Select your ' + NTH[i] +
                                          'card: ', (lambda x: 1 <= x <= max_val),
                                          'You must enter a number between 1 and '
                                          + str(max_val) + '.')
        if game_state.submit(player, selection):
            break
        print(COLORS['ERROR'] + 'You already played this card! '
                                'Choose another card to play.')


def player_turn(blanks: int, player: Player):
    """ Simulate a non-judge player's turn by asking them to select white
        cards from their hand. If they choose a wildcard, they will be
        asked to submit text for the card.

    :param blanks: number of white cards submissions needed
    :param player: the player trying to submit a card
    """
    asciiGraphics.print_player_hand(player.hand)
    offset = 1 if blanks > 1 else 0
    for i in range(blanks):
        try:
            submit_valid_card(player, i + offset)
        except Wildcard as e:
            text = interface.wildcard()
            game_state.submit_wildcard(player, text, e.index)
    game_state.draw_cards(player)
    # TODO: catch OutOfWhiteCards


def judge_turn(player: Player):
    """ Simulate a judge's turn by asking them to select
        a winning submission.

    :param player: the judge
    :return: (winning player, winning card set)
    """
    selection = interface.judge_pick(len(game_state.submissions), player.name)
    return game_state.select_winner(selection)


def play_round():
    """ Simulate one round of the game by every non-judge player
        submitting white cards, and the judge selecting a winner.
        Display the scoreboard at the end of the round, and check
        if a player has won.
    """
    (judge, players), black_card = game_state.new_round()
    for player in players:
        print(DIVIDER + '\n' + judge.name + ' is judging: ')
        asciiGraphics.print_black_card(black_card)
        print(player.name + '\'s hand:\n')
        player_turn(black_card.numBlanks, player)
        print()
    print(DIVIDER + '\n')
    asciiGraphics.print_black_card(black_card)
    asciiGraphics.print_submissions(game_state.get_submissions())
    winner, winning_cards = judge_turn(judge)
    print('\n' + winner.name + ' won with ' + str(winning_cards) + '!\n' + game_state.get_scores())
    if game_state.is_game_over():
        raise GameOver(winner)


def init(state=None):
    """ Setup a new game. May initialize a new state or reuse state
        from a previous game. Play rounds until a player has won.

    :param state: existing game state
    """
    global game_state
    if state is None:
        game_state = State(loader.loadWhiteCards('white_cards_roomies.csv'),
                           loader.loadBlackCards('black_cards_roomies.csv'))
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
