import sys, json
from icecream import ic
from board import Board
from connect import Connection
from player import RandomPlayer


def main(args):
    print("Tablut client")
    ic(args)

    # script path + (role port ip)
    if len(args) != 4:
        print("WRONG NUMBER OF ARGUMENTS")
        return -1

    role = args[1]
    port = args[2]
    ip = args[3]

    ic(f"Role: {role}")

    conn = Connection(ip, port)

    b = Board()

    b.print_grid()

    player = RandomPlayer(role="BLACK", board=b)
    player.play()

    conn.close()

    return 0

if __name__ == "__main__":
    args = sys.argv
    sys.exit(main(args))
