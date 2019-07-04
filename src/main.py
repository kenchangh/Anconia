import sys
import logging
import threading
import time
import argparse

from proto import messages_pb2
from message_server import MessageServer
from message_client import MessageClient
from discovery_server import DiscoveryServer
from gentx import create_random_transactions

logger = logging.getLogger('main')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


class Anconia:
    def start(self, host='127.0.0.1', port=5000, analytics=False,
              adversarial=False, generate_random_tx=True, pubkey='123', nickname='abc'):
        message_client = MessageClient(
            host=host, port=port, analytics=analytics)
        message_server = MessageServer(message_client, host=host, port=port)
        discovery_server = DiscoveryServer(
            message_client, host, port, nickname)

        try:
            discovery_server.start()

            if generate_random_tx:
                create_random_transactions(message_client, adversarial)
            message_server.start()

        except (KeyboardInterrupt, SystemExit):
            message_client.shutdown()
            discovery_server.shutdown()
            sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging turned on')
    parser.add_argument(
        '--host', '-x', type=str, help='Starts the RPC server with this host', default='127.0.0.1')
    parser.add_argument(
        '--port', '-p', type=int, help='Starts the RPC server with this port', default=5000)
    parser.add_argument(
        '--analytics', '-a', type=bool, help='Starts the RPC server with analytics reporting', default=False)
    parser.add_argument(
        '--adversarial', '-z', type=bool, help='Starts the blockchain with adversarial network conditions', default=False)

    parser.add_argument('--randomtx', dest='randomtx', action='store_true')
    parser.add_argument('--no-randomtx', dest='randomtx', action='store_false')
    parser.set_defaults(randomtx=True)

    args = parser.parse_args(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    anconia = Anconia()
    anconia.start(host=args.host, port=args.port,
                  analytics=args.analytics, adversarial=args.adversarial,
                  generate_random_tx=args.randomtx)
