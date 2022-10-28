import socket
from icecream import ic

class Connection:
    def __init__(self, ip, port, timeout=60):
        """
        Create a new UDP connection to the given IP address and Port number

        :param ip: IP address
        :param port: port number
        :param timeout: socket timeout (default 60)
        """

        self.port = port
        self.ip = ip
        #FIXME: ACTUALLY THIS SHOULD USE TCP (Chesani spreads fake news on the internet)
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.socket.bind((self.ip, self.port))
        self.socket.settimeout(timeout)
        self.buffer_size = 1024
        ic(f"Connected to: {ip}:{port}")

    def send(self, data_buf) -> int:
        """
        Send data string

        :param data_buf: string to be sent
        :return: number of bytes sent (-1 on failure)
        """
        sent = self.socket.sendto(str.encode(data_buf), (self.ip, self.port))

        if sent == 0:
            ic("SOCKET CONNECTION BROKEN! (sending)")
            sent = -1

        return ic(sent)

    def receive(self) -> str | None:
        """
        Wait to receive data from server

        :return: the response as a string - None if timed out or connection got broken
        """
        output = None

        try:
            output = self.socket.recvfrom(self.buffer_size)[0]

            if output == b'':
                ic("SOCKET CONNECTION BROKEN! (receiving)")
            else:
                output = str(output)

        except TimeoutError:
            ic("SOCKET TIMED OUT!")

        return ic(output)

    def close(self):
        """
        Close socket connection. Note that the socket will be unusable afterwards!
        """

        self.socket.close()

if __name__ == "__main__":
    conn = Connection("127.0.0.1", 5800, timeout=300)
    ic("lessgo")
    conn.send("OSTIA PATACCA LOMO")

    conn.receive()