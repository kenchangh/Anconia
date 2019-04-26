import socket
import struct
import binascii
from threading import Thread
import logging
from proto import messages_pb2


JOIN_MESSAGE_TYPE = 0
TRANSACTION_MESSAGE_TYPE = 1


class MessageServer:
    def __init__(self, consensus_algorithm):
        self.consensus_algorithm = consensus_algorithm
        self.sock = None
        self.logger = logging.getLogger('main')
        self.peers = set([])
        self.address = None
        self.port = None

    def bind_to_open_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.listen(1)
        address, port = sock.getsockname()
        self.sock = sock
        self.address = address
        self.port = port
        return address, port

    def start(self):
        address, port = self.bind_to_open_port()
        listener_thread = Thread(
            target=self.listen_to_messages, args=(self.sock,))
        listener_thread.start()
        return address, port

    def handle_message(self, raw_msg):
        common_msg = messages_pb2.CommonMessage()
        common_msg.ParseFromString(raw_msg)
        print(common_msg)

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        conn, _ = sock.accept()
        with conn:
            while True:
                try:
                    raw_msg, _ = conn.recvfrom(1024)
                    self.handle_message(raw_msg)
                except socket.error as e:
                    raise e

    def add_peer(self, join_msg):
        new_peer = (join_msg.address, join_msg.port)
        self.peers.add(new_peer)
        self.logger.info(f'Added new peer {join_msg.address}:{join_msg.port}')
