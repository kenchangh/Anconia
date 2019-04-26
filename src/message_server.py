import socket
import struct
import binascii
from threading import Thread
import logging
from proto import peerbook_pb2


class MessageServer:
    def __init__(self):
        self.sock = None
        self.conn = None
        self.logger = logging.getLogger('main')

    def bind_to_open_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.listen(1)
        address, port = sock.getsockname()
        self.sock = sock
        return address, port

    def start(self):
        address, port = self.bind_to_open_port()
        listener_thread = Thread(
            target=self.listen_to_messages, args=(self.sock,))
        listener_thread.start()
        return address, port

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        conn, _ = sock.accept()
        with conn:
            while True:
                try:
                    data = conn.recvfrom(1024)
                    print(data)
                except socket.error as e:
                    raise e
