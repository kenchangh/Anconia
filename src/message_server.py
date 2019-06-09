import sys
import socket
import struct
import binascii
from threading import Thread
import logging
from concurrent.futures import ThreadPoolExecutor
import socketserver
import traceback
from proto import messages_pb2
from message_client import MessageClient
from common import COLOR_MAP, exponential_backoff


class MessageServer:
    def __init__(self, message_client, host=None, port=None):
        self.message_client = message_client
        self.sock = None
        self.logger = logging.getLogger('main')
        self.peers = set([])
        self.address = host
        self.port = port
        self.listener_thread = None
        self.thread_executor = ThreadPoolExecutor(max_workers=8)

    def bind_to_open_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_to = ('', 0)
        if self.address and self.port:
            connect_to = (self.address, self.port)

        sock.bind(connect_to)
        sock.listen(16)
        address, port = sock.getsockname()

        self.sock = sock
        self.address = address
        self.port = port
        return address, port

    def start(self):
        try:
            address, port = self.bind_to_open_port()
            self.listen_to_messages(self.sock)
        except (KeyboardInterrupt, SystemExit):
            self.thread_executor.shutdown(wait=False)
            sys.exit()
        return address, port

    def start_connection_thread(self, conn):
        try:
            # raw_msg = exponential_backoff(
            #     self.logger, conn.recv,
            #     (1024,), timeout=0.01, max_retry=5)
            raw_msg = conn.recv(1024)
            if raw_msg:
                response = self.handle_message(raw_msg)
                if response:
                    # exponential_backoff(
                    #     self.logger, conn.sendall,
                    #     (response,), timeout=0.01, max_retry=5)
                    conn.sendall(response)
            conn.close()
        except socket.error:
            # self.logger.error(e)
            # traceback.print_exc()
            pass

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        while True:
            conn, _ = sock.accept()
            self.thread_executor.submit(self.start_connection_thread, conn)
        sock.close()

    def handle_message(self, raw_msg):
        try:
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
        except Exception as e:
            traceback.print_exc()

    def handle_transaction(self, txn_msg):
        self.logger.info('Received transaction')
        self.message_client.dag.receive_transaction(txn_msg)
        # self.message_client.run_consensus(txn_msg.color)

    def handle_node_query(self, query_msg):
        response_color = None
        if self.message_client.color == messages_pb2.NONE_COLOR:
            response_color = query_msg.color
            with self.message_client.lock:
                self.message_client.color = response_color
            # self.message_client.run_consensus(response_color)
        else:
            response_color = self.message_client.color
        response_query = messages_pb2.NodeQuery()
        response_query.color = response_color
        msg = MessageClient.create_message(
            messages_pb2.NODE_QUERY_MESSAGE, response_query)
        return msg

    def add_peer(self, join_msg):
        new_peer = (join_msg.address, join_msg.port)
        with self.message_client.lock:
            self.message_client.add_peer(new_peer)
