import sys
import time
import socket
import binascii
import params
from threading import Thread
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from japronto import Application
from common import MCAST_GRP, MCAST_PORT, exponential_backoff, simulate_network_latency
from message_client import MessageClient
from proto import messages_pb2


class DiscoveryServer:
    def __init__(self, message_client, host, port, nickname=''):
        self.logger = logging.getLogger('main')
        self.host = host
        self.port = port
        self.nickname = nickname
        self.message_client = message_client
        self.thread_executor = ThreadPoolExecutor(max_workers=8)

    def start(self):
        listener_thread = Thread(target=self.listen_multicast)
        listener_thread.setDaemon(True)
        listener_thread.start()
        joiner_thread = Thread(
            target=self.delayed_multicast_join,
            args=(params.DISCOVERY_STARTUP_DELAY, self.host, self.port))
        joiner_thread.setDaemon(True)
        joiner_thread.start()

    def shutdown(self):
        self.thread_executor.shutdown(wait=False)

    def create_join_message(self, ack=False):
        join_msg = messages_pb2.Join()
        join_msg.address = self.host
        join_msg.port = self.port
        join_msg.pubkey = self.message_client.keypair.pubkey.to_string().hex()
        join_msg.nickname = self.nickname

        if ack:
            join_msg.join_type = messages_pb2.Join.ACK_JOIN
        else:
            join_msg.join_type = messages_pb2.Join.INIT_JOIN

        msg = MessageClient.create_message(messages_pb2.JOIN_MESSAGE, join_msg)
        return msg

    def delayed_multicast_join(self, delay=5, *args):
        time.sleep(delay)
        self.multicast_join(*args)

    def multicast_join(self, address, port):
        msg = self.create_join_message()
        with socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            sock.sendto(msg, (MCAST_GRP, MCAST_PORT))
            self.logger.info('Multicasted JOIN message to ' +
                             MCAST_GRP+':'+str(MCAST_PORT))
            simulate_network_latency()

    def listen_multicast(self):
        self.logger.info('Listening to multicast ' +
                         MCAST_GRP+':'+str(MCAST_PORT))
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        sock.bind((MCAST_GRP, MCAST_PORT))
        host = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                        socket.inet_aton(host))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))

        while True:
            data, _ = sock.recvfrom(1024)
            self.thread_executor.submit(
                self.handle_multicast_message, data)

    def handle_multicast_message(self, data):
        try:
            common_msg = messages_pb2.CommonMessage()
            common_msg.ParseFromString(data)

            join_msg = messages_pb2.Join()
            join_msg.CopyFrom(common_msg.join)
            peer = (join_msg.address, join_msg.port)

            # ignore self
            if join_msg.address == self.host and join_msg.port == self.port:
                return

            with self.message_client.lock:
                self.message_client.add_peer(peer)
            ack_msg = self.create_join_message(ack=True)
            self.message_client.send_message(peer, ack_msg)

        except socket.error:
            common_msg = messages_pb2.CommonMessage()
            common_msg.ParseFromString(data)
            print(f"""{traceback.print_exc()}

My_Host = {self.host}
My_Port = {self.port}
Data = {data}
Parsed = {common_msg}
            """)
