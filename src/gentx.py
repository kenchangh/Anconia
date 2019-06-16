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
        messages = []
        for _ in range(100):
            recipient_addr = random.choice(
                message_client.state.get_all_addresses())
            msg_obj = message_client.generate_txn_object(recipient_addr, 100)
            msg = MessageClient.create_message(
                messages_pb2.TRANSACTION_MESSAGE, msg_obj)
            messages.append(msg)

        for msg in messages:
            # thread_pool.submit(message_client.broadcast_message, msg)
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
