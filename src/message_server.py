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

        message_handlers = {
            messages_pb2.JOIN: ('Join', 'join', self.add_peer),
            messages_pb2.TRANSACTION: ('Transaction', 'transaction', self.handle_transaction),
        }

        handler = message_handlers.get(common_msg.message_type)
        if not handler:
            raise ValueError(
                f"There is no message type {common_msg.message_type}")

        message_classname, attr_name, handler_function = handler
        sub_msg = getattr(messages_pb2, message_classname)()
        sub_msg.CopyFrom(getattr(common_msg, attr_name))
        handler_function(sub_msg)

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        while True:
            conn, _ = sock.accept()
            with conn:
                try:
                    raw_msg = conn.recv(1024)
                    if raw_msg:
                        self.handle_message(raw_msg)
                except socket.error as e:
                    raise e

    def broadcast_message(self, msg):
        for addr, port in self.peers:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print('Connecting to', addr, port)
                s.connect((addr, port))
                s.sendall(msg)
                data = s.recv(1024)

    def handle_transaction(self, txn_msg):
        self.logger.info('Received transaction')
        self.consensus_algorithm(self, txn_msg)

    def add_peer(self, join_msg):
        new_peer = (join_msg.address, join_msg.port)
        self.peers.add(new_peer)
        self.logger.info(f'Added new peer {join_msg.address}:{join_msg.port}')
