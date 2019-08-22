import socket
import pickle
import interface
import asciiGraphics
import colorama
import signal
from constants import BUFF_SIZE, COMMANDS, CMD_SPLIT, ENCODING, COLORS, NTH
from typing import List


def send_msg(msg):
    return sock.sendall(str(msg).encode(ENCODING))


def recv_msg():
    msg: str = sock.recv(BUFF_SIZE).decode(ENCODING)
    return msg.strip()


def recv_obj():
    while True:
        raw_data = sock.recv(BUFF_SIZE)
        data = raw_data.strip()
        if len(data) > 0:
            return pickle.loads(data)


def welcome():
    interface.printCoverArt()


def kill():
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


def judge(hand: List[List[str]]):
    print()
    asciiGraphics.print_submissions(hand)
    selection = interface.judge_pick(len(hand), 'NAME')
    send_msg(selection)


def winner(winner_name: str, winning_cards: str, is_me: bool):
    if is_me:
        print(COLORS['WIN'] + 'You won with ' + winning_cards)
    else:
        interface.print_username(winner_name)
        print(' won with ' + winning_cards)


def parse_command(msg: str):
    data = msg.split(CMD_SPLIT)
    cmd = int(data[0])
    args = data[1:]

    if cmd == COMMANDS['WELCOME']:
        welcome()
    elif cmd == COMMANDS['PLAINTEXT']:
        print(args[0])
    elif cmd == COMMANDS['NAME']:
        enter_name()
    elif cmd == COMMANDS['PLAYER_JOINED']:
        interface.player_joined(args[1], int(args[0]))
    elif cmd == COMMANDS['START_PLAYER_TURN']:
        # order: judge_name, black_card_text, hand
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
        judge(recv_obj())
    elif cmd == COMMANDS['WINNER']:
        winner(args[0], args[1], bool(args[2]))
    elif cmd == COMMANDS['BLACK_CARD']:
        print_black_card(args[0])
    elif cmd == COMMANDS['KILL']:
        kill()
    else:
        print('unknown action')


def start():
    global sock
    host = socket.gethostname()
    port = 8080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    while True:
        data = recv_msg()
        if len(data) > 0:
            parse_command(data)


def force_exit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    sock.close()
    exit(1)


if __name__ == '__main__':
    colorama.init(autoreset=True)
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, force_exit)
    start()
