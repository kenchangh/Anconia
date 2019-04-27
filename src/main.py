import sys
import logging
import threading
import time
import argparse

from proto import messages_pb2
from message_server import MessageServer
from message_client import MessageClient
from discovery_server import DiscoveryServer
from consensus import slush_algorithm

logger = logging.getLogger('main')


class Anconia:
    def start(self, host=None, port=None):
        message_client = MessageClient(consensus_algorithm=slush_algorithm)
        message_client.schedule_transaction()

        message_server = MessageServer(message_client, host=host, port=port)
        message_server.start()

        pubkey = '123'
        nickname = 'abc'
        discovery_server = DiscoveryServer(
            message_server, pubkey, nickname)
        discovery_server.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging turned on')
    parser.add_argument(
        '--host', '-a', type=str, help='Starts the RPC server with this host')
    parser.add_argument(
        '--port', '-p', type=int, help='Starts the RPC server with this port')
    args = parser.parse_args(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    anconia = Anconia()
    anconia.start(host=args.host, port=args.port)
