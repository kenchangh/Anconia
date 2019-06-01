import sys
import time
import random
from message_client import MessageClient
from threading import Thread
from consensus import slush_algorithm
from common import COLOR_MAP, INVERSE_COLOR_MAP


def create_transaction(addr, port, color_str, amount=100):
    color_int = INVERSE_COLOR_MAP.get(color_str)
    if not color_int:
        return ValueError(f'No such color "{color_str}"')

    client = MessageClient(
        consensus_algorithm=slush_algorithm, light_client=True)
    msg = client.generate_transaction(color_int, amount)
    client.send_message((addr, port), msg)


def _create_random_transactions(message_client):
    while True:
        color = random.choice(list(COLOR_MAP.keys()))
        msg = message_client.generate_transaction(color, 100)
        message_client.broadcast_message(msg)
        time.sleep(5)


def create_random_transactions(message_client):
    thread = Thread(target=_create_random_transactions, args=(message_client,))
    thread.start()


if __name__ == '__main__':
    addr = sys.argv[1]
    port = int(sys.argv[2])
    color = sys.argv[3]
    create_transaction(addr, port, color)
