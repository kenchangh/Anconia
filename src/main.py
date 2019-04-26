import logging
import threading
import time

from proto import messages_pb2
from message_server import MessageServer
from message_client import MessageClient
from discovery_server import DiscoveryServer
from consensus import slush_algorithm

logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO)


class Anconia:
    def start(self):
        message_client = MessageClient(consensus_algorithm=slush_algorithm)
        message_client.schedule_transaction()

        message_server = MessageServer(message_client)
        message_server.start()

        pubkey = '123'
        nickname = 'abc'
        discovery_server = DiscoveryServer(
            message_server, pubkey, nickname)
        discovery_server.start()


if __name__ == '__main__':
    anconia = Anconia()
    anconia.start()
