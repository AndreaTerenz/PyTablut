import sys
from argparse import ArgumentParser
from time import time

from icecream import ic

from Tablut import Tablut
from aima.games import GameState, alpha_beta_cutoff_search, alpha_beta_search
from board import Board, CheckerType
from connect import Connection, get_player_port
from gui import GUI
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
    ui = GUI()
    b.print_grid()
    ui.draw(b)

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

        for i in range(8):
            # Alternate black and white
            turn = player.role if (i % 2) == 0 else player.opponent

            print(f"--------{turn}--------")
            tablut.board = b
            tablut.role = turn
            culo = GameState(to_move=turn, utility=tablut.utility(b, turn), board=b, moves=tablut.actions(b))

            print("Initial board:")
            b.print_grid()

            print("Searching move...")
            before = time()
            if depth <= 0:
                move = alpha_beta_search(culo, tablut)
            else:
                move = alpha_beta_cutoff_search(culo, tablut, depth)
            after = time()
            _from, _to = move[0], move[1]

            new_board = b.apply_move(_from, _to, turn)

            ## Various sanity checks
            try:

                all_equal = True
                for i in range(9):
                    for j in range(9):
                        if b.grid[i, j] != new_board.grid[i, j]:
                            all_equal = False
                            break
                    if not all_equal:
                        break

                assert not all_equal, "WHY THE HECK ARE THE TWO BOARDS IDENTICAL??"

                for move in culo.moves:
                    # every element in culo.moves is a [from, to] move,
                    # where "from" and "to" are two tuples
                    f, t = move
                    # check that every move in culo.moves is actually possible
                    assert b.grid[t].checker == CheckerType.EMPTY, \
                        f"ILLEGAL MOVE IN LIST OF POSSIBLE MOVES: {f} -> {t}"

                expected_checker = [CheckerType.WHITE, CheckerType.KING] if turn == "WHITE" else [CheckerType.BLACK]
                assert b.grid[_from].checker in expected_checker, \
                    f"ILLEGAL STARTING POSITION: {_from} ({b.grid[_from].checker})"
                assert b.grid[_to].checker == CheckerType.EMPTY, \
                    f"ILLEGAL FINAL POSITION: {_to} ({b.grid[_to].checker})"
            except AssertionError as e:
                print("CRITICAL ERROR")
                print(e)
                return -1
            ##

            b = new_board

            print(f"Move found: {move[0]} -> {move[1]}")
            print(f"Search took {(after - before):.3f} s")

            print("Resulting board:")
            b.print_grid()
            ui.draw(b)

    return 0

if __name__ == "__main__":
    sys.exit(main())
