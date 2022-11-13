import sys
from argparse import ArgumentParser
from time import time

from Tablut import Tablut
from aima.games import GameState, alpha_beta_cutoff_search
from board import CheckerType
from connect import get_player_port
from gui import GUI

CLIENT_NAME = "StreetKing"


def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument("role", help="Player role (either 'BLACK' or 'WHITE')", choices=["BLACK", "WHITE"])
    parser.add_argument("-p", "--port", help="Server connection port (defaults to 5800 for WHITE and 5801 for BLACK)",
                        type=int)
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


def run_tests(old_board, new_board, moves, _from, _to, turn):
    # Check that the new board is actually different
    all_equal = True
    for i in range(9):
        for j in range(9):
            if old_board.grid[i, j] != new_board.grid[i, j]:
                all_equal = False
                break
        if not all_equal:
            break

    assert not all_equal, "WHY THE fuck ARE THE TWO BOARDS IDENTICAL??"

    # check that list of checkers for the current turn has been updated
    old_checkers = old_board.get_checkers_for_role(turn)
    new_checkers = new_board.get_checkers_for_role(turn)
    all_equal = (set(old_checkers) == set(new_checkers))
    assert not all_equal, "WHY THE fuck ARE THE CHECKERS LISTS IDENTICAL??"

    for move in moves:
        # every element in culo.moves is a [from, to] move,
        # where "from" and "to" are two tuples
        f, t = move
        # check that every move in culo.moves is actually possible
        assert old_board.grid[t].checker == CheckerType.EMPTY, \
            f"ILLEGAL POSSIBLE MOVE: {f} -> {t}"

    expected_checker = [CheckerType.WHITE, CheckerType.KING] if turn == "WHITE" else [CheckerType.BLACK]
    assert old_board.grid[_from].checker in expected_checker, \
        f"ILLEGAL STARTING POSITION: {_from} ({old_board.grid[_from].checker})"
    assert old_board.grid[_to].checker == CheckerType.EMPTY, \
        f"ILLEGAL FINAL POSITION: {_to} ({old_board.grid[_to].checker})"


def main():
    print(CLIENT_NAME)

    role, ip, port, skip_conn, depth = parse_arguments()
    opponent = "BLACK" if role == "WHITE" else "WHITE"

    print(f"Role: {role}")
    print(f"Minmax depth: {depth}")
    print(f"Run locally? {skip_conn}")

    print("#####################################")

    if not skip_conn:
        print(f"IP address: {ip}")
        print(f"TCP port: {port}")
        """
        conn = Connection(CLIENT_NAME, role, server_ip=ip, server_port=port)
        b = Board()
        player = RandomPlayer(role, b)
        try:
            conn.connect_to_server()
        except:
            return -1

        
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
        """
    else:
        ui = GUI(title=CLIENT_NAME)
        tablut = Tablut(role)
        tablut.board.print_grid()
        ui.draw(tablut.board)

        print("#####################################")

        i = 0
        for i in range(20):
            kr, kc = tablut.board.king
            if kr == 100 or kc == 100:
                break

            # Alternate black and white
            turn = role if (i % 2) == 0 else opponent

            print(f"--------{turn}--------")
            tablut.role = turn
            culo = GameState(to_move=turn,
                             utility=tablut.utility(tablut.board, turn),
                             board=tablut.board,
                             moves=tablut.actions(tablut.board))

            print("Initial board:")
            tablut.board.print_grid()

            print("Searching move...")
            before = time()
            move = alpha_beta_cutoff_search(culo, tablut, depth)
            after = time()
            _from, _to = move[0], move[1]

            new_board = tablut.board.apply_move(_from, _to, turn)

            ## Run some sanity checks
            try:
                run_tests(tablut.board, new_board, culo.moves, _from, _to, turn)
            except AssertionError as e:
                print("[CRITICAL ERROR]")
                print(e)
                return -1

            tablut.board = new_board

            print(f"Move: {move[0]} -> {move[1]}")
            print(f"Found in: {(after - before):.3f} s")

            print("Resulting board:")
            tablut.board.print_grid()
            ui.draw(tablut.board)

        print("#####################################")
        print(f"GAME OVER ({i + 1} turns)")
        tablut.board.print_grid()

    return 0

if __name__ == "__main__":
    sys.exit(main())
