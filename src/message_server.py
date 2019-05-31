import socket
import struct
import binascii
from threading import Thread
import logging
import multiprocessing
import socketserver
from proto import messages_pb2
from message_client import MessageClient
from common import COLOR_MAP


class MessageServer:
    def __init__(self, message_client, host=None, port=None):
        self.message_client = message_client
        self.sock = None
        self.logger = logging.getLogger('main')
        self.peers = set([])
        self.address = host
        self.port = port
        self.listener_thread = None

    def bind_to_open_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_to = ('', 0)
        if self.address and self.port:
            connect_to = (self.address, self.port)

        sock.bind(connect_to)
        sock.listen(1)
        address, port = sock.getsockname()

        self.sock = sock
        self.address = address
        self.port = port
        return address, port

    def start(self):
        address, port = self.bind_to_open_port()
        self.listen_to_messages(self.sock)
        # self.listener_thread = Thread(
        #     target=self.listen_to_messages, args=(self.sock,))
        # self.listener_thread.start()
        return address, port

    def start_connection_thread(self, conn):
        try:
            raw_msg = b''
            while True:
                fragment = conn.recv(1024)
                if not fragment:
                    break
                raw_msg += fragment

            if raw_msg:
                response = self.handle_message(raw_msg)
                if response:
                    conn.sendall(response)
            conn.close()
        except socket.error as e:
            self.logger.error(e)

    def listen_to_messages(self, sock):
        address, port = sock.getsockname()
        self.logger.info(f'Listening to messages on {address}:{port}')
        while True:
            conn, _ = sock.accept()
            self.start_connection_thread(conn)
        sock.close()
