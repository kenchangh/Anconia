import socket
import binascii
from threading import Thread
import logging
from common import MCAST_GRP, MCAST_PORT


class DiscoveryServer:
    def __init__(self):
        self.logger = logging.getLogger('main')

    def start(self):
        self.multicast_join()
        listener_thread = Thread(target=self.listen_multicast)
        listener_thread.start()

    def multicast_join(self):
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.sendto(b'Hello World!', (MCAST_GRP, MCAST_PORT))
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
                data, addr = sock.recvfrom(1024)
                print(data, addr)
            except socket.error as e:
                print('Expection')
                hexdata = binascii.hexlify(data)
                print('Data = %s' % hexdata)
