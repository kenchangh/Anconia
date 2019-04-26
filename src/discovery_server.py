import socket
import binascii
from threading import Thread
import logging
from common import MCAST_GRP, MCAST_PORT
from message_client import MessageClient
from proto import messages_pb2


class DiscoveryServer:
    def __init__(self, message_server, pubkey, nickname=''):
        self.logger = logging.getLogger('main')
        self.message_server = message_server
        self.pubkey = pubkey
        self.nickname = nickname

    def start(self):
        self.multicast_join(self.message_server.address,
                            self.message_server.port)
        listener_thread = Thread(target=self.listen_multicast)
        listener_thread.start()

    def create_join_message(self, ack=False):
        join_msg = messages_pb2.Join()
        join_msg.address = self.message_server.address
        join_msg.port = self.message_server.port
        join_msg.pubkey = self.pubkey
        join_msg.nickname = self.nickname

        if ack:
            join_msg.join_type = messages_pb2.Join.ACK_JOIN
        else:
            join_msg.join_type = messages_pb2.Join.INIT_JOIN

        msg = MessageClient.create_message(messages_pb2.JOIN_MESSAGE, join_msg)
        return msg

    def multicast_join(self, address, port):
        msg = self.create_join_message()
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.sendto(msg, (MCAST_GRP, MCAST_PORT))
        self.logger.info('Multicasted JOIN message to ' +
                         MCAST_GRP+':'+str(MCAST_PORT))

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
            try:
                data, _ = sock.recvfrom(1024)
                common_msg = messages_pb2.CommonMessage()
                common_msg.ParseFromString(data)

                join_msg = messages_pb2.Join()
                join_msg.CopyFrom(common_msg.join)
                self.message_server.add_peer(join_msg)

                ack_msg = self.create_join_message(ack=True)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((join_msg.address, join_msg.port))
                    s.sendall(ack_msg)
                    data = s.recv(1024)
            except socket.error as e:
                print(e)
                # hexdata = binascii.hexlify(data)
                print(f'Data = {data}')
