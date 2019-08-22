import socket
import signal
import pickle
import loader
import interface
from constants import BUFF_SIZE, COMMANDS, CMD_SPLIT, ENCODING
from state import State, BlackCard, Player
from exceptions import *
from threading import Thread, Barrier

MAX_PLAYERS = 3
global server, clients
game = State(loader.loadWhiteCards('white_cards.csv'),
             loader.loadBlackCards('black_cards.csv'))


def send_msg(cmd: int, conn=None, data=None, except_id=None):
    msg = str(cmd) + CMD_SPLIT
    if data is not None:
        msg += data
    if conn is not None:
        conn.sendall(msg.encode(ENCODING))
        conn.sendall((' '*BUFF_SIZE).encode(ENCODING))
    else:
        for id in clients.keys():
            if id != except_id:
                try:
                    clients[id].sendall(msg.encode(ENCODING))
                    clients[id].sendall((' ' * BUFF_SIZE).encode(ENCODING))
                except BrokenPipeError:
                    pass


def send_obj(conn, data):
    conn.sendall(pickle.dumps(data))


def split_msg_data(data):
    if len(data) == 0:
        return ''
    else:
        s = str(data[0])
        for item in data[1:]:
            s += CMD_SPLIT + str(item)
        return s


def recv_msg(conn):
    return conn.recv(BUFF_SIZE).decode(ENCODING)


def connect_client(sock: socket, addr: str, barrier: Barrier):
    global clients
    send_msg(COMMANDS['NAME'], sock)
    name = recv_msg(sock)
    send_msg(COMMANDS['PLAYER_JOINED'], data=split_msg_data([0, name]))
    send_msg(COMMANDS['PLAYER_JOINED'], sock,
             split_msg_data([1, game.pretty_player_names()]))
    player_id = len(clients)
    clients[player_id] = sock
    game.add_player(name, player_id)
    interface.player_joined(name)

    barrier.wait()
    send_msg(COMMANDS['WELCOME'], sock)


def receive_submission(sock, player: Player, black_card, judge: Player,
                       offset: int):
    try:
        while True:
            card_num = int(recv_msg(sock))
            if game.submit(player, card_num):
                break
            send_msg(COMMANDS['PLAY_CARD_AGAIN'], sock)
            send_msg(COMMANDS['PLAY_CARD'], sock,
                     split_msg_data([len(player.hand), offset]))
    except Wildcard as e:
        send_msg(COMMANDS['WILDCARD'], sock)
        text = recv_msg(sock)
        game.submit_wildcard(player, text, e.index)


def player_turn(sock, barrier, player, black_card: BlackCard, judge):
    offset = 1 if black_card.numBlanks > 1 else 0
    original_hand = list(player.hand)
    data = [judge.name, black_card.text]
    data.extend(original_hand)
    send_msg(COMMANDS['START_PLAYER_TURN'], sock, split_msg_data(data))

    for i in range(black_card.numBlanks):
        send_msg(COMMANDS['PLAY_CARD'], sock,
                 split_msg_data([len(player.hand), i + offset]))
        receive_submission(sock, player, black_card, judge, i + offset)

    send_msg(COMMANDS['PLAINTEXT'], sock,
             'You played ' + str(game.submissions[player]))
    game.draw_cards(player)
    send_msg(COMMANDS['PLAYED'], clients[judge.id], player.name)
    barrier.wait()


def judge_turn(sock, judge):
    send_msg(COMMANDS['JUDGE'], sock)
    subs = game.get_submissions()
    y = [[str(card) for card in x]for x in subs]
    send_obj(sock, y)
    selection = int(recv_msg(sock))
    return game.select_winner(selection)


def play_round():
    (judge, players), black_card = game.new_round()
    barrier = Barrier(len(players))
    player_threads = []
    send_msg(COMMANDS['BLACK_CARD'], clients[judge.id], str(black_card))
    send_msg(COMMANDS['PLAINTEXT'], clients[judge.id],
             'You\'re judging- wait for everyone to play')
    for player in players:
        thread = Thread(target=player_turn,
                        args=(clients[player.id], barrier, player,
                              black_card, judge))
        thread.setDaemon(True)
        player_threads.append(thread)
        thread.start()

    for thread in player_threads:
        thread.join()
    winner, winning_cards = judge_turn(clients[judge.id], judge)
    print(winner, winning_cards)
    send_msg(COMMANDS['WINNER'], data=split_msg_data([winner.name, winning_cards, 0]), except_id=winner.id)
    send_msg(COMMANDS['WINNER'], conn=clients[winner.id], data=split_msg_data(['', winning_cards, 1]))


def start():
    global server, clients
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = {}
    threads = []
    barrier = Barrier(MAX_PLAYERS)

    print('Connected to ' + ip + ':' + str(port))
    server.bind((ip, port))
    server.listen(MAX_PLAYERS)
    for i in range(MAX_PLAYERS):
        conn, addr = server.accept()
        client_thread = Thread(target=connect_client,
                               args=(conn, addr, barrier,))
        client_thread.setDaemon(True)
        threads.append(client_thread)
        client_thread.start()

    for thread in threads:
        thread.join()

    play_round()
    kill_clients()
    server.close()


def kill_clients():
    send_msg(COMMANDS['KILL'])


def force_exit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    kill_clients()
    server.close()
    exit(1)


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, force_exit)
    start()
