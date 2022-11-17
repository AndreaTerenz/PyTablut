import sys
from argparse import ArgumentParser
from time import time

from icecream import ic

from Tablut import Tablut
from aima.games import GameState, alpha_beta_cutoff_search
from board import CheckerType
from connect import get_player_port
from gui import GUI

CLIENT_NAME = "topG"


def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument("role", help="Player role (either 'BLACK' or 'WHITE')", choices=["BLACK", "WHITE"])
    parser.add_argument("-p", "--port", help="Server connection port (defaults to 5800 for WHITE and 5801 for BLACK)",
                        type=int)
    parser.add_argument("-i", "--ip", help="Server IP address (defaults to localhost)", default="localhost")
    parser.add_argument("-l", "--local", help="Do not connect to server and run player against itself locally",
                        action="store_true")
    parser.add_argument("-t", "--max-turns", help="Maximum number of turns for local game (implies --local)",
                        default=-1, type=int)
    parser.add_argument("-d", "--depth",
                        help="Minmax tree maximum depth (default is 3, value <= 0 to ignore depth cutoff)", default=3,
                        type=int)
    parser.add_argument("--skip-connection",
                        help="[DEPRECATED, USE --local] If provided, ignore failed connection to server",
                        action="store_true")

    args = parser.parse_args()

    skip_conn = bool(args.local or (args.max_turns > 0) or args.skip_connection)

    port = args.port
    if not port:
        port = get_player_port(args.role)

    return args.role, args.ip, port, skip_conn, args.depth, args.max_turns


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

    role, ip, port, skip_conn, depth, max_turns = parse_arguments()
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
        print(f"Max number of turns per player: {max_turns}")

        ui = GUI(title=CLIENT_NAME)
        tablut = Tablut(role)
        tablut.board.print_grid()
        ui.draw(tablut.board)

        print("#####################################")

        ic.disable()
        i = 0
        for i in range(max_turns * 2):
            # Alternate black and white
            turn = role if (i % 2) == 0 else opponent

            print(f"----------------{turn} (turn {i})")

            print("Initial board:")
            tablut.board.print_grid()

            done = False
            esc = tablut.board.available_escape()
            before = after = time()

            if turn == "WHITE" and esc != (-1, -1):
                print(f"Escape cell available in {esc}")
                move = tablut.board.king, esc
                done = True
            else:
                tablut.role = turn
                culo = GameState(to_move=turn,
                                 utility=tablut.utility(tablut.board, turn),
                                 board=tablut.board,
                                 moves=tablut.actions(tablut.board))

                print("Searching move...")
                before = time()
                move = alpha_beta_cutoff_search(culo, tablut, depth)
                after = time()

            assert not move is None, "WHAT DO YOU MEAN MOVE IS NONE???"

            _from, _to = move[0], move[1]

            new_board = tablut.board.apply_move(_from, _to, turn)

            tablut.board = new_board

            print(f"Move: {move[0]} -> {move[1]}")
            print(f"Found in: {(after - before):.3f} s")

            print("Resulting board:")
            tablut.board.print_grid()
            ui.draw(tablut.board)

            if done:
                break

            # sleep(1)

        print("#####################################")
        print(f"GAME OVER ({i + 1} turns)")
        tablut.board.print_grid()

    return 0

if __name__ == "__main__":
    sys.exit(main())
