import sys, json
from icecream import ic
from board import Board
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

    print(f"Role: {role}")
    print(f"Connecting to: {ip}:{port}")

    b = Board()
    
    print("Initial state:")
    b.print_grid()

    player = RandomPlayer(role="BLACK", board=b)
    #player.play()

    def print_grid(board_copy):
        for i in range(1,10):
            for j in range(1,10):
                print(f"{board_copy.grid[i][j].type.value};{board_copy.grid[i][j].checker.value} ", end=" ")
            print()

    b_update = player.self_update()
    print("Final state after eating:")
    print_grid(b_update)

    return 0

if __name__ == "__main__":
    args = sys.argv
    sys.exit(main(args))
