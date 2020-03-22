import socket
import signal
import pickle
import loader
import interface
from constants import BUFF_SIZE, COMMANDS, CMD_SPLIT, ENCODING, DIVIDER, \
    VALID, COLORS, DEFAULT_BLACK_CARDS, DEFAULT_WHITE_CARDS, DEFAULT_PORT
from state import State, BlackCard, Player
from exceptions import *
from threading import Thread, Barrier

MAX_PLAYERS = 3
global server, clients


def send_msg(cmd: int, conn=None, data=None, except_id=None):
    msg = str(cmd) + CMD_SPLIT
    if data is not None:
        msg += data
    if conn is not None:
        try:
            conn.sendall(msg.encode(ENCODING))
            conn.sendall((' '*BUFF_SIZE).encode(ENCODING))
        except BrokenPipeError:
            pass
    else:
        for id in clients.keys():
            if id != except_id:
                try:
                    clients[id].sendall(msg.encode(ENCODING))
                    clients[id].sendall((' ' * BUFF_SIZE).encode(ENCODING))
                except BrokenPipeError:
                    pass


def send_obj(data, conn=None, except_id=None):
    obj = pickle.dumps(data)
    if conn is None:
        for id in clients.keys():
            if id != except_id:
                try:
                    clients[id].sendall(obj)
                except BrokenPipeError:
                    pass
        pass
    else:
        try:
            conn.sendall(obj)
        except BrokenPipeError:
            pass


# def send_art_line(data: str, conn=None, except_id=None):
#     if conn is None:
#         for id in clients.keys():
#             if id != except_id:
#                 clients[id].sendall(data.encode(ENCODING))
#                 clients[id].sendall((' ' * BUFF_SIZE).encode(ENCODING))
#         pass
#     else:
#         conn.sendall(data.encode(ENCODING))
#         conn.sendall((' ' * BUFF_SIZE).encode(ENCODING))


def split_msg_data(data):
    if len(data) == 0:
        return ''
    else:
        s = str(data[0])
        for item in data[1:]:
            s += CMD_SPLIT + str(item)
        return s


def recv_msg(conn):
    try:
        msg = conn.recv(BUFF_SIZE).decode(ENCODING)
        if msg == str(COMMANDS['KILL']):
            raise ConnectionResetError
        return msg
    except ConnectionResetError:
        player = None
        for p in game.players:
            if clients[p.id] == conn:
                player = p
        raise PlayerDisconnected(player)


def receive_submission(sock, player: Player, offset: int):
    try:
        while True:
            card_num = int(recv_msg(sock))
            if game.submit(player, card_num):
                break
            send_msg(COMMANDS['PLAY_CARD_AGAIN'], sock)
            send_msg(COMMANDS['PLAY_CARD'], sock,
                     split_msg_data([len(player.hand), offset]))
    except PlayerDisconnected as e:
        player_disconnected(e)
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
        receive_submission(sock, player, i + offset)

    send_msg(COMMANDS['PLAINTEXT'], sock,
             'You played ' + str(game.submissions[player]) + '\n\n' +
             DIVIDER + '\n\nWaiting for other players...')
    game.draw_cards(player)
    send_msg(COMMANDS['PLAYED'], clients[judge.id], player.name)
    barrier.wait()


def judge_turn(sock, judge):
    send_msg(COMMANDS['JUDGE'], data=split_msg_data([judge.name, 0]),
             except_id=judge.id)
    send_msg(COMMANDS['JUDGE'], sock, data=split_msg_data([judge.name, 1]))
    send_obj([[str(card) for card in x]for x in game.get_submissions()])
    try:
        selection = int(recv_msg(sock))
        return game.select_winner(selection)
    except PlayerDisconnected as e:
        player_disconnected(e)


def play_round():
    (judge, players), black_card = game.new_round()
    barrier = Barrier(len(players))
    player_threads = []
    send_msg(COMMANDS['BLACK_CARD'], clients[judge.id], str(black_card))
    send_msg(COMMANDS['PLAINTEXT'], clients[judge.id],
             'You are the judge- waiting for everyone to play...')
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
    send_msg(COMMANDS['WINNER'],
             data=split_msg_data([winner.name, winning_cards, 0]),
             except_id=winner.id)
    send_msg(COMMANDS['WINNER'], conn=clients[winner.id],
             data=split_msg_data(['', winning_cards, 1]))
    send_msg(COMMANDS['PLAINTEXT'], data='SCOREBOARD\n'+game.get_scores()+'\n'+DIVIDER+'\n')
    if game.is_game_over():
        raise GameOver(winner)


def connect_client(sock: socket, barrier: Barrier):
    global clients
    send_msg(COMMANDS['NAME'], sock)
    try:
        name = recv_msg(sock)
        send_msg(COMMANDS['PLAYER_JOINED'], data=split_msg_data([0, name]))
        send_msg(COMMANDS['PLAYER_JOINED'], sock,
                 split_msg_data([1, game.pretty_player_names()]))
        player_id = len(clients)
        clients[player_id] = sock
        game.add_player(name, player_id)
        interface.player_joined(name)
        barrier.wait()
    except PlayerDisconnected as e:
        pass


def get_address():
    """ The IP address and port to host the server on

    :return: (ip address, port number)
    """
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = DEFAULT_PORT
    return ip, port


def setup_server(ip, port):
    global clients, game, server

    # initialize game state
    game = State(loader.loadWhiteCards(DEFAULT_WHITE_CARDS),
                 loader.loadBlackCards(DEFAULT_BLACK_CARDS))

    # bind socket to address
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))

    clients = {}
    threads = []
    barrier = Barrier(MAX_PLAYERS)

    server.listen(MAX_PLAYERS)
    for i in range(MAX_PLAYERS):
        try:
            conn, addr = server.accept()
            client_thread = Thread(target=connect_client,
                                   args=(conn, barrier,))
            client_thread.setDaemon(True)
            threads.append(client_thread)
            client_thread.start()
        except ConnectionAbortedError:
            pass

    for thread in threads:
        thread.join()


def init(game_state=None):
    global server, clients, game
    ip, port = get_address()
    print(COLORS['PROMPT'] + 'Connected to ' + ip + ':' + str(port))

    # if a game isn't already setup, set up a game state and server
    # otherwise, use existing state and server
    if game_state is None:
        setup_server(ip, port)

    send_msg(COMMANDS['ART'])

    # send_msg(COMMANDS['ART'], data='COVER_ART')
    # cover_art_lines = loader.loadArt('art/coverArt.txt')
    # for line in cover_art_lines:
    #     print(line)
    #     send_art_line(CMD_SPLIT + line + CMD_SPLIT)
    # send_art_line(CMD_END)

    while True:
        try:
            play_round()
        except GameOver as e:
            send_msg(COMMANDS['WON_GAME'], data=split_msg_data([e.player.name, 0]),
                     except_id=e.player.id)
            send_msg(COMMANDS['WON_GAME'], conn=clients[e.player.id],
                     data=split_msg_data(['', 1]))
            break
    game.reset()

    x = input('Do you want to play again? [Y/n]: ').strip()
    try:
        if x == '' or VALID[x]:
            init(game)
        kill_clients()
        server.close()
    except:
        kill_clients()
        server.close()


def kill_clients():
    send_msg(COMMANDS['KILL'])


def player_disconnected(ex):
    if ex.player is None:
        print(COLORS['ERROR'] + 'Player disconnected')
        server.close()
    else:
        print(COLORS['USERNAME'] + ex.player.name, end='')
        print(COLORS['ERROR'] + ' disconnected')
        server.close()


def force_exit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    kill_clients()
    server.close()
    exit(1)


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, force_exit)
    init()
