import logging
import threading
import time

from proto import messages_pb2
from message_server import MessageServer
from discovery_server import DiscoveryServer
from consensus import slush_algorithm
from common import create_message

logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO)


class Anconia:
    def start(self):
        message_server = MessageServer(
            consensus_algorithm=slush_algorithm)
        self.message_server = message_server
        message_server.start()

        pubkey = '123'
        nickname = 'abc'
        discovery_server = DiscoveryServer(
            message_server, pubkey, nickname)
        discovery_server.start()

        txn_thread = threading.Thread(target=self.create_transaction)
        txn_thread.start()
        txn_thread.join()

    def create_transaction(self):
        time.sleep(2)
        common_msg = messages_pb2.CommonMessage()
        txn_msg = messages_pb2.Transaction()
        txn_msg.color = messages_pb2.BLUE_COLOR
        txn_msg.amount = 100
        msg = create_message(messages_pb2.TRANSACTION_MESSAGE, txn_msg)
        self.message_server.broadcast_message(msg)
        logger.info('Sent transaction')


if __name__ == '__main__':
    anconia = Anconia()
    anconia.start()
