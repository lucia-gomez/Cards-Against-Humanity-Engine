import socket
import pickle
import interface
import asciiGraphics
import colorama
import signal
from constants import BUFF_SIZE, COMMANDS, CMD_SPLIT, ENCODING, \
    COLORS, NTH, DIVIDER, DEFAULT_PORT
from typing import List


def send_msg(msg):
    return sock.sendall(str(msg).encode(ENCODING))


def recv_msg():
    msg: str = sock.recv(BUFF_SIZE).decode(ENCODING)
    return msg.strip()


# def recv_art():
#     art = ''
#     while True:
#         raw_line: str = sock.recv(BUFF_SIZE).decode(ENCODING, errors='ignore')
#         line = raw_line.split(CMD_SPLIT)
#         if len(line) > 2:
#             data = line[1]
#             if CMD_END in data:
#                 return art + data.strip(CMD_END)
#             art += data


def recv_obj():
    while True:
        raw_data = sock.recv(BUFF_SIZE)
        data = raw_data.strip()
        if len(data) > 0:
            return pickle.loads(data)


def print_art(color: str):
    interface.printCoverArt()


def kill():
    print()
    print(COLORS['ERROR'] + 'The server has been shutdown')
    sock.close()
    exit(0)


def enter_name():
    name = interface.validateString('Enter a username: ', 30).upper()
    if send_msg(name) is None:
        print(COLORS['PROMPT'] + 'Connected')


def play_card(max_val, n):
    card = interface.validateInt('Select your ' + NTH[int(n)] + 'card: ',
                                 (lambda x: 1 <= x <= int(max_val)),
                                 'Enter a number between 1 and ' +
                                 max_val + '.')
    send_msg(card)


def start_player_turn(judge_name, black_card_text, hand):
    interface.print_username(judge_name)
    print(' is judging\n')
    print_black_card(black_card_text)
    print()
    asciiGraphics.print_player_hand(hand)


def wildcard():
    text = interface.wildcard()
    send_msg(text)


def play_again():
    print(COLORS['ERROR'] + 'You already played this card! '
                            'Choose another card to play.')


def player_played(name):
    interface.print_username(name)
    print(' has played')


def print_black_card(text):
    asciiGraphics.print_black_card(text)


def judge(hand: List[List[str]], judge_name: str, is_me: int):
    print('\nEveryone has played!\n')
    asciiGraphics.print_submissions(hand)
    if is_me:
        selection = interface.judge_pick(len(hand), judge_name)
        send_msg(selection)
    else:
        print('Judge ', end='')
        interface.print_username(judge_name)
        print(' is choosing the winner...')


def winner(winner_name: str, winning_cards: str, is_me: int):
    if is_me:
        print(COLORS['WIN'] + 'You won with ' + winning_cards)
    else:
        interface.print_username(winner_name)
        print(' won with ' + winning_cards)
    print()


def won_game(winner_name: str, is_me: int):
    print()
    if is_me:
        print(COLORS['WIN'] + 'YOU WON THE GAME!')
    else:
        interface.print_username(winner_name)
        print(' won the game!')
    print('\n' + DIVIDER + '\n')


def parse_command(msg: str):
    data = msg.split(CMD_SPLIT)
    cmd = int(data[0])
    args = data[1:]

    if cmd == COMMANDS['ART']:
        print_art(args[0])
    elif cmd == COMMANDS['PLAINTEXT']:
        print(args[0])
    elif cmd == COMMANDS['NAME']:
        enter_name()
    elif cmd == COMMANDS['PLAYER_JOINED']:
        interface.player_joined(args[1], int(args[0]))
    elif cmd == COMMANDS['START_PLAYER_TURN']:
        start_player_turn(args[0], args[1], args[2:])
    elif cmd == COMMANDS['PLAY_CARD']:
        play_card(args[0], args[1])
    elif cmd == COMMANDS['WILDCARD']:
        wildcard()
    elif cmd == COMMANDS['PLAYED']:
        player_played(args[0])
    elif cmd == COMMANDS['PLAY_CARD_AGAIN']:
        play_again()
    elif cmd == COMMANDS['JUDGE']:
        judge(recv_obj(), args[0], int(args[1]))
    elif cmd == COMMANDS['WINNER']:
        winner(args[0], args[1], int(args[2]))
    elif cmd == COMMANDS['WON_GAME']:
        won_game(args[0], int(args[1]))
    elif cmd == COMMANDS['BLACK_CARD']:
        print_black_card(args[0])
    elif cmd == COMMANDS['KILL']:
        kill()
    else:
        print('unknown action')


def start():
    global sock
    # TODO: prompt the user for address
    host = socket.gethostname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, DEFAULT_PORT))
    except ConnectionRefusedError:
        print(COLORS['ERROR'] + 'The server is offline')
        exit(0)
    while True:
        data = recv_msg()
        if len(data) > 0:
            parse_command(data)


def force_exit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    send_msg(COMMANDS['KILL'])
    sock.close()
    exit(1)


if __name__ == '__main__':
    colorama.init(autoreset=True)
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, force_exit)
    start()
