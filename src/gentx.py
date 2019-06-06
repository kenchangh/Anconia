import sys
import time
import random
from message_client import MessageClient
from threading import Thread
from consensus import snowball_algorithm
from common import COLOR_MAP, INVERSE_COLOR_MAP


def _create_random_transactions(message_client):
    while True:
        recipient_addr = random.choice(
            message_client.state.get_all_addresses())
        msg = message_client.generate_transaction(recipient_addr, 100)
        message_client.broadcast_message(msg)
        time.sleep(5)


def create_random_transactions(message_client):
    thread = Thread(target=_create_random_transactions, args=(message_client,))
    thread.setDaemon(True)
    thread.start()
