import sys
from argparse import ArgumentParser
from icecream import ic
from board import Board
from connect import Connection, get_player_port
from player import RandomPlayer

CLIENT_NAME = "Besugo"

def main():
    ic("Tablut client")

    ####
    # Reading command line arguments

    parser = ArgumentParser()

    parser.add_argument("role", help="Player role (either 'BLACK' or 'WHITE')")
    parser.add_argument("-p", "--port", help="Server connection port (defaults to 5800 for WHITE and 5801 for BLACK)", type=int)
    parser.add_argument("-i", "--ip", help="Server IP address (defaults to localhost)", default="localhost")
    parser.add_argument("--skip-connection", help="If provided, ignore failed connection to server (useful in debug/development)", action="store_true")

    args = parser.parse_args()

    role = args.role
    ip = args.ip

    port = args.port
    if not port:
        port = get_player_port(role)

    ic(role, ip, port)

    ####

    conn = Connection(CLIENT_NAME, role, server_ip=ip, server_port=port)

    if not args.skip_connection:
        try:
            conn.connect_to_server()
        except:
            return -1
    else:
        ic("Connection to server skipped")

    b = Board()
    player = RandomPlayer(role, b)

    b.print_grid()

    player.play()

    """
    Game loop:
    
    while [game not over]:
        1) get player move M
        2) send move to server
        3) receive opponent move M'
        4) update board with M'
    """

    conn.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
