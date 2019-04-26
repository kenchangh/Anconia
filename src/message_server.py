import socket
import struct
import binascii
from threading import Thread
import logging
from proto import messages_pb2
from message_client import MessageClient


class MessageServer:
    def __init__(self, message_client):
        self.color = messages_pb2.NONE_COLOR
        self.message_client = message_client
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

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        while True:
            conn, _ = sock.accept()
            with conn:
                try:
                    raw_msg = conn.recv(1024)
                    if raw_msg:
                        response = self.handle_message(raw_msg)
                        if response:
                            conn.sendall(response)
                    conn.close()
                except socket.error as e:
                    raise e

    def handle_message(self, raw_msg):
        common_msg = messages_pb2.CommonMessage()
        common_msg.ParseFromString(raw_msg)

        message_handlers = {
            messages_pb2.JOIN_MESSAGE: ('Join', 'join', self.add_peer),
            messages_pb2.TRANSACTION_MESSAGE: ('Transaction', 'transaction', self.handle_transaction),
            messages_pb2.NODE_QUERY_MESSAGE: (
                'NodeQuery', 'node_query', self.handle_node_query),
        }

        handler = message_handlers.get(common_msg.message_type)
        if not handler:
            raise ValueError(
                f"There is no message type {common_msg.message_type} or handler not created yet")

        message_classname, attr_name, handler_function = handler
        sub_msg = getattr(messages_pb2, message_classname)()
        sub_msg.CopyFrom(getattr(common_msg, attr_name))
        return handler_function(sub_msg)

    def handle_transaction(self, txn_msg):
        self.logger.info('Received transaction')
        self.message_client.run_consensus(txn_msg)

    def handle_node_query(self, query_msg):
        response_color = None
        if self.color == messages_pb2.NONE_COLOR:
            response_color = query_msg.color
        else:
            response_color = self.color
        response_query = messages_pb2.NodeQuery()
        response_query.color = response_color
        msg = MessageClient.create_message(
            messages_pb2.NODE_QUERY_MESSAGE, query_msg)
        return msg

    def add_peer(self, join_msg):
        new_peer = (join_msg.address, join_msg.port)
        self.message_client.add_peer(new_peer)
