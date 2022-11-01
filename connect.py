# https://github.com/ancaah/TablutPlayer/blob/b43853ea2c6a1bff0f9315eeaa229434e39ef965/tools.py

import json
import socket
import struct
from icecream import ic
from player import BasePlayer


class Connection:

    # According to the server code, it will use these two ports to
    # communicate with the corresponding players
    WHITE_PORT = 5800
    BLACK_PORT = 5801

    def __init__(self, player_name: str, player_color: str, server_ip="localhost", timeout=60):
        """
        Create a new connection to the game server

        :param player_name: Player name to use for the game
        :param player_color: Player color ("BLACK" or "WHITE")
        :param server_ip: Server IP address to connect to (defaults to localhost)
        :param timeout: Socket timeout in seconds (defaults to 60)
        :raises ConnectionFailedError: The connection can't be established
        """

        self.ip = server_ip
        self.port = Connection.WHITE_PORT if player_color == "WHITE" else Connection.BLACK_PORT

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.settimeout(timeout)

        try:
            self.socket.connect((self.ip, self.port))
            ic(f"Connected to: {self.ip}:{self.port}")
            self.__send_string(player_name)
        except socket.error as e:
            ic(f"CONNECTION FAILED! ({e})")
            self.socket = None
            raise ConnectionFailedError(self.ip, self.port, player_name, player_color)

    def send_move(self, from_pos: tuple[int], to_pos: tuple[int], player_obj: BasePlayer):
        """
        Send a move to the server.

        :param from_pos: Move starting cell
        :param to_pos: Move destination cell
        :param player_obj: BasePlayer object (used to determine color - BLACK or WHITE)
        """

        # Encode the input parameters into a dictionary and transform it into a JSON string
        data = json.dumps({
            "from": encode_grid_pos(from_pos),
            "to": encode_grid_pos(to_pos),
            "turn": player_obj.role,
        })

        self.__send_string(data)

    def __send_string(self, string: str):
        """
        Helper function to properly send a string to the server (it has to be preceded
        by its length)

        :param string: data string to send
        """

        # Using struct lib in order to represent data as python bytes objects
        # struct.pack(format, val1, val2...)
        # '>i' means Big Endian(used in network), integer returns a bytes object.
        self.socket.send(struct.pack('>i', len(string)))
        self.socket.send(string.encode())

    def __receive_bytes(self, n):
        """
        Receive N bytes from server or None if EOF is hit

        :param n: max number of bytes to receive
        :return: received data or None if failed
        """
        data = b''

        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet

        return data

    def receive_new_state(self):
        """
        Receive updated board state from server

        :return: Board state as grid
        """

        response_len = struct.unpack('>i', self.__receive_bytes(4))[0]
        server_response = self.socket.recv(response_len)

        return extract_board_state(server_response)

    def close(self):
        """
        Close socket connection. Note that the socket will be unusable afterwards!
        """

        self.socket.close()

def extract_board_state(json_str):
    """
    Take the data received from the server as a string and extract the updated board state

    :param json_str: Server response data
    :return: The board state as a grid - None if it can't be found
    """

    data = json.loads(json_str)
    return data.get("board")

def encode_grid_pos(pos : tuple[int]) -> str:
    """
    Encodes a [row]-[column] position into a [letter][number] string, where the letter corresponds to the column
    and the number is the row index (plus 1). This is the encoding required by the server.
    E.g., "h1" corresponds to row 0 and column 7.

    :param pos: Position to encode
    :return: Encoded position as string
    """

    row, col = pos[0], pos[1]
    # 97 is the value of 'a' (column #0) in the ASCII table
    # The chr(n) method converts and ASCII code to its corresponding carachter
    return f"{chr(97 + col)}{1+row}"

class ConnectionFailedError(Exception):
    def __init__(self, ip, port, name, color):
        self.ip = ip
        self.port = port
        self.name = name
        self.color = color

if __name__ == "__main__":
    pass