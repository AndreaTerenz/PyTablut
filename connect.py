# https://github.com/ancaah/TablutPlayer/blob/b43853ea2c6a1bff0f9315eeaa229434e39ef965/tools.py

import json
import socket
import struct

from icecream import ic


class Connection:
    # According to the server code, it will use these two ports to
    # communicate with the corresponding players
    WHITE_PORT = 5800
    BLACK_PORT = 5801

    def __init__(self, player_name: str, player_color: str, server_ip="localhost", server_port=None, timeout=60):
        """
        Create a new connection to the game server

        :param player_name: Player name to use for the game
        :param player_color: Player color ("BLACK" or "WHITE")
        :param server_ip: Server IP address to connect to (defaults to localhost)
        :param server_port: Server port number to connect to (if omitted, it will be determined from the player_color)
        :param timeout: Socket timeout in seconds (defaults to 60)
        """
        self.name = player_name
        self.color = player_color
        self.ip = server_ip
        self.port = server_port if server_port else get_player_port(self.color)

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.settimeout(timeout)

    def connect_to_server(self):
        """
        Attempts to connect to the game server

        :raises ConnectionFailedError: The connection can't be established
        :returns: True if the connection attempt was successful
        """
        try:
            self.socket.connect((self.ip, self.port))
            # ic(f"Connected to {self.ip}:{self.port} as {self.color} player")
            return self.__send_string(self.name)
        except socket.error as e:
            #ic(f"CONNECTION FAILED! ({e})")
            self.socket = None
            return False

    def send_move(self, from_pos: tuple[int], to_pos: tuple[int]):
        """
        Send a move to the server.

        :param from_pos: Move starting cell
        :param to_pos: Move destination cell
        :returns: True if the move was sent successfully
        """

        # Encode the input parameters into a dictionary and transform it into a JSON string
        data = json.dumps({
            "from": encode_grid_pos(from_pos),
            "to": encode_grid_pos(to_pos),
            "turn": self.color,
        })

        return self.__send_string(data)

    def __send_string(self, string: str):
        """
        Helper function to properly send a string to the server (it has to be preceded
        by its length)

        :param string: data string to send
        :returns: True if the string was sent successfully
        :raises ConnectionError:
        """

        try:
            # Using struct lib in order to represent data as python bytes objects
            # struct.pack(format, val1, val2...)
            # '>i' means Big Endian(used in network), integer returns a bytes object.
            self.socket.send(struct.pack('>i', len(string)))
            self.socket.send(string.encode())
        except ConnectionError as ce:
            raise ce

        return True

    def __receive_bytes(self, n):
        """
        Receive N bytes from server or None if EOF is hit

        :param n: max number of bytes to receive
        :return: received data or None if failed
        :raises ConnectionResetError: Connection was broken before all data could be received
        """
        data = b''

        while len(data) < n:
            packet = self.socket.recv(ic(n) - len(data))

            if not ic(packet):
                return None
            data += packet
        return data

    def receive_new_state(self):
        """
        Receive updated board state from server

        :return: Board state as grid
        """

        bytes = self.__receive_bytes(4)
        response_len = struct.unpack('>i', ic(bytes))[0]
        server_response = self.socket.recv(response_len)

        data = json.loads(server_response)

        return data.get("board"), data.get("turn")

    def close(self):
        """
        Close socket connection. Note that the socket will be unusable afterwards!
        """
        if self.socket:
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

    row, col = ic(pos)[0], pos[1]
    # 97 is the value of 'a' (column #0) in the ASCII table
    # The chr(n) method converts and ASCII code to its corresponding carachter
    return ic(f"{chr(97 + col)}{1 + row}")

def get_player_port(color: str) -> int:
    """
    "Converts" the player color ("BLACK" or "WHITE") to its corresponding port number (5801 or 5800)

    :param color: player's color
    :return: port number
    """

    return Connection.WHITE_PORT if color == "WHITE" else Connection.BLACK_PORT