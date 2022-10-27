import socket
from icecream import ic

class Connection:
    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.settimeout(90)
        self.buffer_size = 1024
        ic(f"Connected to: {ip}:{port}")

    def send(self, data_buf):
        self.socket.sendto(str.encode(data_buf), (self.ip, self.port))

    def receive(self):
        try:
            msg = self.socket.recvfrom(self.buffer_size)[0]

            return ic(msg)
        except TimeoutError:
            ic("SOCKET TIMED OUT!")
            return None