import sys, json
from icecream import ic
from board import Board

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

    b.print_grid()

    # Read test json file
    with open("test_board.json", "r") as test_json:
        response = json.load(test_json)
        b.update_state(response["board"])
    print("AAAAAAAAAAAAAA")
    b.print_grid()

    return 0

if __name__ == "__main__":
    args = sys.argv
    sys.exit(main(args))
