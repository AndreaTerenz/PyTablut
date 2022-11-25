import sys
from argparse import ArgumentParser
from time import time

from icecream import ic

from Tablut import Tablut
from connect import get_player_port, Connection
from gui import GUI

CLIENT_NAME = "topG"

# Exit error codes
FAILED_CONN_ERR = 1
FAILED_SYNC_ERR = 2
BROKEN_PIPE_ERR = 3
CONN_RESET_ERR = 4
STATE_UPDATE_ERR = 5
CONN_TIMEOUT_ERR = 6

errors = {
    FAILED_CONN_ERR: "Connection failed (Is the server running?)",
    FAILED_SYNC_ERR: "Sync not received",
    BROKEN_PIPE_ERR: "Broken connection",
    CONN_RESET_ERR: "Connection reset by peer",
    STATE_UPDATE_ERR: "Failed to receive update",
    CONN_TIMEOUT_ERR: "Connection timed out",
}


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

    args = parser.parse_args()

    if args.local and args.max_turns <= 0:
        args.max_turns = 200

    skip_conn = bool(args.local or (args.max_turns > 0))

    port = args.port
    if not port:
        port = get_player_port(args.role)

    return args.role, args.ip, port, skip_conn, args.depth, args.max_turns

def run_locally(role, opponent, max_turns, minmax_depth):
    print(f"Max number of turns per player: {max_turns}")

    ui = GUI(title=CLIENT_NAME)
    tablut = Tablut(role)
    tablut.board.print_grid()
    ui.draw(tablut.board)

    print("#####################################")

    i = 0
    for i in range(max_turns * 2):
        # Alternate black and white
        turn = role if (i % 2) == 0 else opponent

        print(f"----------------{turn} (turn {i})")

        print("Initial board:")
        tablut.board.print_grid()

        done = False
        escapes = tablut.board.available_escapes()
        before = after = time()

        if turn == "WHITE" and len(escapes) > 0:
            print(f"Escape cell available in {escapes[0]}")
            move = tablut.board.king, escapes[0]
            done = True
        else:
            print("Searching move...")
            before = time()
            tablut.role = turn
            move = tablut.search_move(minmax_depth)
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

def quit_game(connection, exit_code=0, msg=""):
    """
    Simple function to handle quitting, both with a proper game over
    and in case of errors

    :param connection: Connection object (to be closed before quitting)
    :param exit_code: Program exit code (default 0)
    :param msg: Optional additional message to be printed (ideally, winning player if exit_code==0 and error message if exit_code!=0 - default "")
    """

    if not msg in ["WHITE", "BLACK"] and msg != "":
        print(msg)
    elif exit_code == 0:
        print(f"{msg} wins")
    else:
        print(f"FAILURE - {errors[exit_code]}")

    print("GAME OVER")

    connection.close()

    sys.exit(exit_code)

def main():
    ic.disable()

    role, ip, port, skip_conn, minmax_depth, max_turns = parse_arguments()
    opponent = "BLACK" if role == "WHITE" else "WHITE"

    print(f"##################################### {CLIENT_NAME} TABLUT CLIENT")
    print(f"Role: {role}")
    print(f"Minmax depth: {minmax_depth}")
    print(f"Run locally? {skip_conn}")

    print("#####################################")

    if not skip_conn:
        print(f"IP address: {ip}")
        print(f"TCP port: {port}")

        conn = Connection(CLIENT_NAME, role, server_ip=ip, server_port=port)

        print("Connecting to server...", end="", flush=True)
        if not conn.connect_to_server():
            quit_game(conn, exit_code=FAILED_CONN_ERR)
        else:
            print("Connected")

        tablut = Tablut(role)

        print("Waiting for sync...", end="", flush=True)
        if not conn.receive_new_state():
            quit_game(conn, exit_code=FAILED_SYNC_ERR)

        print("Received")
        print("STARTING GAME")

        print("#####################################")

        i = 0
        while True:
            # WHITE plays on even turns, BLACK on odd
            turn = "WHITE" if i % 2 == 0 else "BLACK"
            print(f"----------{turn} [{'me' if turn == role else 'opponent'} - turn #{i}]")

            if turn == role:
                tablut.board.print_grid(title="Current board:")

                print("Searching move...", end="", flush=True)

                before = time()
                move = tablut.search_move(minmax_depth)
                print(move)
                after = time()

                f, t = move
                tablut.board = tablut.board.apply_move(f, t, role)

                print(f"found: {f} -> {t}")
                print(f"search took: {(after - before):.3f} s")

                tablut.board.print_grid(title="Updated board:")
                print("Sending nudes...", end="", flush=True)

                # Did you manage to send the move?
                try:
                    conn.send_move(f, t)
                    print(f"sent")
                except BrokenPipeError:
                    quit_game(conn, exit_code=BROKEN_PIPE_ERR)
                except ConnectionResetError:
                    quit_game(conn, exit_code=CONN_RESET_ERR)
                ##########

            elif turn == opponent:
                print("Waiting for opponent move...", end="", flush=True)
                received = None

                # Did you receive the next game state?
                try:
                    received = conn.receive_new_state()
                    # Having to do this is kinda gay ngl
                    while ic(received[1]) == opponent:
                        received = conn.receive_new_state()

                    print(f"received")
                except ConnectionError:
                    quit_game(conn, exit_code=STATE_UPDATE_ERR)
                except TimeoutError:
                    quit_game(conn, exit_code=CONN_TIMEOUT_ERR)
                ##########

                new_state, next_turn = received

                # Did someone just win?
                if ic(next_turn) in ["WHITEWIN", "BLACKWIN"]:
                    quit_game(conn, msg=str(next_turn).removesuffix("WIN"))
                ##########

                tablut.board.update_state(new_state)
                tablut.board.print_grid(title="Updated board received:")

            i += 1
    else:
        run_locally(role, opponent, max_turns, minmax_depth)

    return 0

if __name__ == "__main__":
    sys.exit(main())
