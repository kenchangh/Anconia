import sys
import time
import random
import params
from message_client import MessageClient
from threading import Thread
from crypto import Keypair
from proto import messages_pb2
from concurrent.futures import ThreadPoolExecutor


def _create_random_transactions(message_client):
    attacker = Keypair()
    # thread_pool = ThreadPoolExecutor(max_workers=8)

    txns_per_tick = params.TPS_BENCHMARK / params.PEERS_COUNT
    total_delay_time = txns_per_tick * params.RANDOM_TX_GENERATION
    txns_per_tick = int(txns_per_tick + total_delay_time)

    while True:
        batch_txns = messages_pb2.BatchTransactions()
        entries = 100

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
        message_client.broadcast_message(msg)


def create_random_transactions(message_client):
    thread = Thread(target=_create_random_transactions, args=(message_client,))
    thread.setDaemon(True)
    thread.start()
