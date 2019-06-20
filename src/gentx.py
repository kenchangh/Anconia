import sys
import time
import random
import params
from message_client import MessageClient
from threading import Thread
from crypto import Keypair
from proto import messages_pb2
from concurrent.futures import ThreadPoolExecutor


def generate_adversarial(message_client, attacker):
    entries = params.TX_GEN_RATE
    batch_txns = messages_pb2.BatchTransactions()
    for i in range(int(entries/2)):
        recipient_addr = random.choice(
            message_client.state.get_all_addresses())
        msg_obj = message_client.generate_txn_object(recipient_addr, 100)
        batch_txns.transactions.append(msg_obj)

    for i in range(int(entries/2)):
        conflict_msg_obj = message_client.generate_conflicting_txn(
            msg_obj, attacker.address, 100)
        batch_txns.transactions.append(conflict_msg_obj)

    msg = MessageClient.create_message(
        messages_pb2.BATCH_TRANSACTIONS_MESSAGE, batch_txns)
    return msg


def generate_virtuous(message_client):
    entries = params.TX_GEN_RATE
    batch_txns = messages_pb2.BatchTransactions()

    for i in range(int(entries)):
        recipient_addr = random.choice(
            message_client.state.get_all_addresses())
        msg_obj = message_client.generate_txn_object(recipient_addr, 100)
        batch_txns.transactions.append(msg_obj)

    msg = MessageClient.create_message(
        messages_pb2.BATCH_TRANSACTIONS_MESSAGE, batch_txns)
    return msg


def _create_random_transactions(message_client, is_adversarial):
    attacker = Keypair()

    while True:
        if message_client.is_shutdown:
            return
        msg = None
        if is_adversarial:
            msg = generate_adversarial(message_client, attacker)
        else:
            msg = generate_virtuous(message_client)
        message_client.broadcast_message(msg)
        # print('len', len(message_client.dag.transactions.keys()))
        time.sleep(params.RANDOM_TX_GENERATION)


def create_random_transactions(message_client, is_adversarial):
    thread = Thread(target=_create_random_transactions,
                    args=(message_client, is_adversarial))
    thread.setDaemon(True)
    thread.start()
