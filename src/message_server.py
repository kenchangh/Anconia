import socket
import struct
from common import MCAST_GRP, MCAST_PORT


class MessageServer:
    def get_open_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        sock.close()
        return port

    def start(self):
        pass
