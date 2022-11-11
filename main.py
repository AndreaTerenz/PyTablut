import sys
from argparse import ArgumentParser
from time import time

from icecream import ic

from Tablut import Tablut
from aima.games import GameState, alpha_beta_cutoff_search, alpha_beta_search
from board import Board
from connect import Connection, get_player_port
from player import RandomPlayer

CLIENT_NAME = "StreetKing"

def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument("role", help="Player role (either 'BLACK' or 'WHITE')", choices=["BLACK", "WHITE"])
    parser.add_argument("-p", "--port", help="Server connection port (defaults to 5800 for WHITE and 5801 for BLACK)", type=int)
    parser.add_argument("-i", "--ip", help="Server IP address (defaults to localhost)", default="localhost")
    parser.add_argument("-l", "--local", help="Do not connect to server and run player against itself locally",
                        action="store_true")
    parser.add_argument("-d", "--depth",
                        help="Minmax tree maximum depth (default is 3, value <= 0 to ignore depth cutoff)", default=3,
                        type=int)
    parser.add_argument("--skip-connection",
                        help="[DEPRECATED, USE --local] If provided, ignore failed connection to server",
                        action="store_true")

    args = parser.parse_args()

    role = args.role
    ip = args.ip
    skip_conn = args.local or args.skip_connection
    depth = args.depth

    port = args.port
    if not port:
        port = get_player_port(role)

    return role, ip, port, skip_conn, depth

def main():
    ic("Tablut client")

    role, ip, port, skip_conn, depth = parse_arguments()

    print(f"Role: {role}")
    print(f"IP address: {ip}")
    print(f"TCP port: {port}")
    print(f"Minmax depth: {depth}")
    print(f"Run locally? {skip_conn}")

    b = Board()
    b.print_grid()

    player = RandomPlayer(role, b)
    tablut = Tablut(player)

    conn = Connection(CLIENT_NAME, role, server_ip=ip, server_port=port)

    if not skip_conn:
        try:
            conn.connect_to_server()
        except:
            return -1

        """
        Game loop:

        while [game not over]:
            1) get player move M
            2) send move to server
            3) receive opponent move M'
            4) update board with M'
        """
        if role == "BLACK":
            new_state = conn.receive_new_state()
            b.update_state(new_state)

        receive_failed = False
        game_over = False
        while not receive_failed and not game_over:
            move = player.play()
            if len(move) == 0:
                # The player can't find any moves to play
                game_over = True
            else:
                f, t = move
                conn.send_move(f, t)
                new_state = conn.receive_new_state()
                receive_failed = new_state is None

                if not receive_failed:
                    b.update_state(new_state)
                    game_over = b.is_game_over()

        ic("Game done!")
        conn.close()
        return 0
    else:
        ic("Connection to server skipped")

        for i in range(6):
            # Alternate black and white
            turn = player.role if (i % 2) == 0 else player.opponent

            print(f"--------{turn}--------")
            tablut.board = b
            tablut.role = turn
            culo = GameState(to_move=turn, utility=tablut.utility(b, turn), board=b, moves=tablut.actions(b))

            print("Searching move...")
            before = time()
            if depth <= 0:
                move = alpha_beta_search(culo, tablut)
            else:
                move = alpha_beta_cutoff_search(culo, tablut, depth)
            after = time()
            _from, _to = move[0], move[1]
            b = b.apply_move(_from, _to, turn)

            print(f"Suggested move: {move} ({after - before} s)")
            b.print_grid()

    return 0

if __name__ == "__main__":
    sys.exit(main())
