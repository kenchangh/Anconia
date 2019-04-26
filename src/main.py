import logging

from message_server import MessageServer
from discovery_server import DiscoveryServer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Anconia:
    def start(self):
        discovery_server = DiscoveryServer()
        message_server = MessageServer()

        discovery_server.start()
        message_server.start()


if __name__ == '__main__':
    anconia = Anconia()
    anconia.start()
