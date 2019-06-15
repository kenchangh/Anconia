import sys
import time
import random
import params
from message_client import MessageClient
from threading import Thread
from crypto import Keypair
from proto import messages_pb2


def _create_random_transactions(message_client):
    attacker = Keypair()

    while True:
        recipient_addr = random.choice(
            message_client.state.get_all_addresses())
        msg_obj = message_client.generate_txn_object(recipient_addr, 100)
        msg = MessageClient.create_message(
            messages_pb2.TRANSACTION_MESSAGE, msg_obj)

        message_client.broadcast_message(msg)
        time.sleep(params.RANDOM_TX_GENERATION)

        # conflict_msg_obj = message_client.generate_conflicting_txn(
        #     msg_obj, attacker.address, 100)
        # conflict_msg = MessageClient.create_message(
        #     messages_pb2.TRANSACTION_MESSAGE, conflict_msg_obj)
        # message_client.broadcast_message(conflict_msg)
        # time.sleep(params.RANDOM_TX_GENERATION)


def create_random_transactions(message_client):
    thread = Thread(target=_create_random_transactions, args=(message_client,))
    thread.setDaemon(True)
    thread.start()
