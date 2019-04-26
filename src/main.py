import logging

from message_server import MessageServer
from discovery_server import DiscoveryServer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Anconia:
    def start(self):
        message_server = MessageServer()
        message_server.start()

        pubkey = '123'
        nickname = 'abc'
        discovery_server = DiscoveryServer(message_server, pubkey, nickname)
        discovery_server.start()


if __name__ == '__main__':
    anconia = Anconia()
    anconia.start()
