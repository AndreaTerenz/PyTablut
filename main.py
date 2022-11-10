import sys
from argparse import ArgumentParser

from icecream import ic

from Tablut import Tablut
from aima.games import GameState, alpha_beta_cutoff_search
from board import Board
from connect import Connection, get_player_port
from player import RandomPlayer

CLIENT_NAME = "StreetKing"

def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument("role", help="Player role (either 'BLACK' or 'WHITE')")
    parser.add_argument("-p", "--port", help="Server connection port (defaults to 5800 for WHITE and 5801 for BLACK)", type=int)
    parser.add_argument("-i", "--ip", help="Server IP address (defaults to localhost)", default="localhost")
    parser.add_argument("--skip-connection", help="If provided, ignore failed connection to server (useful in debug/development)", action="store_true")

    args = parser.parse_args()

    role = args.role
    ip = args.ip
    skip_conn = args.skip_connection

    port = args.port
    if not port:
        port = get_player_port(role)

    return role, ip, port, skip_conn

def main():
    ic("Tablut client")

    role, ip, port, skip_conn = parse_arguments()

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

        print("______________________________________")
        culo = GameState(to_move=player.role, utility=tablut.utility(b, player.role), board=b, moves=tablut.actions(b))
        move = alpha_beta_cutoff_search(culo, tablut, 3)
        print(move)
        _from, _to = move[0], move[1]
        b.print_grid()
        b = b.apply_move(_from, _to, player.role)
        b.print_grid()

        print("______________________________________")
        culo = GameState(to_move=player.role, utility=tablut.utility(b, player.role), board=b, moves=tablut.actions(b))
        move = alpha_beta_cutoff_search(culo, tablut, 3)
        print(move)
        _from, _to = move[0], move[1]
        b.print_grid()
        b = b.apply_move(_from, _to, player.role)
        b.print_grid()
    return 0

if __name__ == "__main__":
    sys.exit(main())
