import socket
import time
import math
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from threading import Lock, RLock, Thread
from proto import messages_pb2
from common import exponential_backoff, simulate_network_latency, redis
from utils import read_genesis_state
from crypto import Keypair
from statedb import StateDB
from dag import DAG
import analytics
import params
import requests

# TO BE UPDATED PERIODICALLY
ATTR_NAMES = {
    messages_pb2.NODE_QUERY_MESSAGE: 'node_query',
    messages_pb2.JOIN_MESSAGE: 'join',
    messages_pb2.TRANSACTION_MESSAGE: 'transaction',
    messages_pb2.SYNC_GRAPH_MESSAGE: 'sync_graph',
    messages_pb2.REQUEST_SYNC_GRAPH_MESSAGE: 'request_sync_graph',
    messages_pb2.BATCH_TRANSACTIONS_MESSAGE: 'batch_transactions',
}


class Peers:
    """
    Peers class that interfaces with the redis db.
    """

    def __init__(self, my_port):
        self.key = f'{my_port}:peers'
        self.my_port = my_port

    def __contains__(self, value):
        peers = self.get()
        return value in peers

    def __len__(self):
        peers = self.get()
        return len(peers)

    def get(self):
        ports = redis.smembers(self.key)
        ports = [int(port) for port in list(ports)]
        peers = set([('127.0.0.1', port) for port in ports])

        # remove self
        myself = ('127.0.0.1', self.my_port)
        if myself in peers:
            peers.remove(myself)
        return peers

    def add(self, peer):
        host, port = peer
        return redis.sadd(self.key, port)

    def remove(self, peer):
        host, port = peer
        return redis.srem(self.key, port)


class MessageClient:
    def __init__(self, host='127.0.0.1', port=5000, analytics=False, light_client=False,own_key=None):
        """
        Client that interacts with other peers in the network.

        light_client=True, to disable peering and storing peer information.
        """
        self.host = host
        self.port = port
        self.is_shutdown = False

        self.state = StateDB()
        self.keypair = Keypair.from_genesis_file(read_genesis_state())

        if own_key:
            self.keypair = own_key

        self.dag = DAG()
        self.peers = Peers(port)
        self.FIXED_PEERS = (('127.0.0.1',5000),('127.0.0.1',5001),('127.0.0.1',5003))
        self.sessions = {}

        self.logger = logging.getLogger('main')
        self.is_light_client = light_client
        self.lock = Lock()

        self.broadcast_executor = ThreadPoolExecutor(max_workers=8)
        self.tx_executor = ThreadPoolExecutor(max_workers=8)
        self.query_executor = ThreadPoolExecutor(max_workers=4)

        self.analytics_enabled = analytics
        self.analytics_doc_id = None

        self.metrics_lock = Lock()
        self.collect_metrics = False
        self.metrics_start = None
        self.metrics_end = None
        self.transactions_count = 0

        self.txn_insert_times = {}

    def shutdown(self):
        self.broadcast_executor.shutdown(wait=False)
        self.tx_executor.shutdown(wait=False)
        self.query_executor.shutdown(wait=False)
        self.is_shutdown = True

    @staticmethod
    def get_sub_message(message_type, message):
        attr_name = ATTR_NAMES.get(message_type)
        if not attr_name:
            raise ValueError(
                f'Invalid message_type {message_type}, or ATTR_NAMES not updated')

        common_msg = messages_pb2.CommonMessage()
        common_msg.ParseFromString(message)
        sub_msg = getattr(common_msg, attr_name)
        return sub_msg

    @staticmethod
    def create_message(message_type, sub_msg):
        common_msg = messages_pb2.CommonMessage()
        common_msg.message_type = message_type

        attr_name = ATTR_NAMES.get(message_type)
        if not attr_name:
            raise ValueError(
                f'Invalid message_type {message_type}, or ATTR_NAMES not updated')

        getattr(common_msg, attr_name).CopyFrom(sub_msg)
        msg = common_msg.SerializeToString()
        return msg
    
    def check_tx_status(self,txhash):
        request_tx = messages_pb2.RequestTransaction()
        request_tx.hash = txhash
        msg = request_tx.SerializeToString()

        peer = self.FIXED_PEERS[0]
        response = self.send_message(peer, msg, path='/txstatus')
        txn = messages_pb2.Transaction()
        txn.ParseFromString(response)
        return txn

    def check_balance(self):
        check_balance = messages_pb2.CheckBalance()
        check_balance.address = self.keypair.nice_address
        msg = check_balance.SerializeToString()

        peer = self.FIXED_PEERS[0]
        response = self.send_message(peer, msg, path='/balance')
        balance_response = messages_pb2.BalanceResponse()
        balance_response.ParseFromString(response)
        return balance_response

    def sync_graph(self):
        thread = Thread(target=self._sync_graph)
        thread.setDaemon(True)
        thread.start()

    def _sync_graph(self):
        time.sleep(params.SYNC_GRAPH_DELAY)

        self.logger.info(
            f'Requesting for graph sync...')

        if self.is_light_client:
            return

        request_sync_msg = messages_pb2.RequestSyncGraph()
        request_sync_msg.address = self.host
        request_sync_msg.port = self.port
        request_sync_msg.pubkey = self.keypair.pubkey.to_string().hex()

        msg = MessageClient.create_message(
            messages_pb2.REQUEST_SYNC_GRAPH_MESSAGE, request_sync_msg)

        peers = self.peers.get()
        responses = []

        for peer in peers:
            response = self.send_message(peer, msg)
            responses.append(response)

        largest_txns_size = 0
        largest_sync_graph = None

        for response in responses:
            common_msg = messages_pb2.CommonMessage()
            common_msg.ParseFromString(response)
            sync_graph = messages_pb2.SyncGraph()
            sync_graph.CopyFrom(common_msg.sync_graph)

            transactions_size = len(sync_graph.transactions)
            if transactions_size > largest_txns_size:
                largest_txns_size = transactions_size
                largest_sync_graph = sync_graph

        if largest_sync_graph:
            self.bootstrap_graph(largest_sync_graph)
            self.logger.info(
                f'Synced graph with {largest_txns_size} transactions')
        else:
            self.logger.info(
                'Aborted sync graph because current node has most updated state')

    def bootstrap_graph(self, sync_graph_msg):
        transactions = {}
        for txn in sync_graph_msg.transactions:
            transactions[txn.hash] = txn

        with self.dag.lock:
            self.dag.transactions.update(transactions)

            for conflict_set in sync_graph_msg.conflicts:
                self.dag.conflicts.add_conflict(*conflict_set.hashes)

            for conflict_set in sync_graph_msg.conflicts:
                first_txn = conflict_set.hashes[0]
                self.dag.decide_on_preference(first_txn)

    def start_query_worker(self):
        if not self.is_light_client:
            thread = Thread(target=self.query_loop)
            thread.setDaemon(True)
            thread.start()

    def query_loop(self):
        running_queries = {}
        accepted = set([])
        while True:
            if self.is_shutdown:
                return
            txn_hashes = tuple(self.dag.transactions.keys())
            for txn_hash in txn_hashes:
                if self.is_shutdown:
                    return
                txn = self.dag.transactions[txn_hash]
                running = running_queries.get(txn_hash)

                if not running:
                    if not txn.queried:
                        running_queries[txn_hash] = True
                        self.query_executor.submit(self.query_txn, txn)
                if txn.queried and not txn.accepted:
                    self.dag.update_accepted(txn)

                if txn.accepted and txn_hash not in accepted:
                    print('ACCEPTED')
                    accepted.add(txn.hash)
                    inserted_time = self.txn_insert_times.get(txn.hash)
                    accepted_time = time.time()

                    if inserted_time:
                        time_taken = accepted_time - inserted_time
                        total_accepted = len(accepted)
                        self.logger.info(
                            f'UPDATE_ACCEPTED: {time_taken} seconds, {total_accepted} txns')

    def select_network_sample(self):
        with self.lock:
            query_nodes = []
            peers = self.peers.get()

            if len(peers) < params.NETWORK_SAMPLE_SIZE:
                query_nodes = list(peers)
            else:
                query_nodes = random.sample(
                    peers, params.NETWORK_SAMPLE_SIZE)
            return query_nodes

    def query_txn(self, txn_msg):
        query_nodes = []
        query_success_threshold = math.floor(
            params.ALPHA_PARAM * params.NETWORK_SAMPLE_SIZE)
        consecutive_count = 0
        iterations = 0
        short_txn_hash = txn_msg.hash[:20]

        while consecutive_count < params.BETA_CONSECUTIVE_PARAM:
            if self.is_shutdown:
                return

            if iterations >= params.MAX_QUERY_ITERATIONS:
                break

            strongly_preferred_count = 0
            query_nodes = self.select_network_sample()
            start_time = time.time()
            end_by_time = start_time + params.QUERY_TIMEOUT

            is_strongly_preferred = self.dag.is_strongly_preferred(txn_msg)
            node_query = messages_pb2.NodeQuery()
            node_query.txn_hash = txn_msg.hash
            node_query.is_strongly_preferred = is_strongly_preferred
            node_query.from_address = self.host
            node_query.from_port = self.port
            msg = MessageClient.create_message(
                messages_pb2.NODE_QUERY_MESSAGE, node_query)

            for node in query_nodes:
                if self.is_shutdown:
                    return

                # exceeded QUERY_TIMEOUT
                if time.time() >= end_by_time:
                    self.logger.error(
                        f'Timeout for query of {short_txn_hash}...')
                    break

                response = self.send_message(node, msg)
                if not response:
                    continue

                query_response = MessageClient.get_sub_message(
                    messages_pb2.NODE_QUERY_MESSAGE, response)
                if query_response.txn_hash != txn_msg.hash:
                    self.logger.error(
                        f"Invalid txn_hash from query response: {short_txn_hash}...")
                    continue

                strongly_preferred_count += query_response.is_strongly_preferred

            # self.logger.info(
            #     f'Received {strongly_preferred_count} strongly-preferred responses for {short_txn_hash}')

            with self.dag.lock:
                if strongly_preferred_count >= query_success_threshold:
                    short_txn_hash = txn_msg.hash[:20]
                    self.logger.info(f'Added chit to {short_txn_hash}')
                    self.dag.transactions[txn_msg.hash].chit = True
                    consecutive_count += 1
                else:
                    self.logger.info(
                        f'Reverted chit of {short_txn_hash} with {strongly_preferred_count} strongly-preferred responses')
                    self.dag.transactions[txn_msg.hash].chit = False
                    consecutive_count = 0

            iterations += 1
            # time.sleep(params.TIME_BETWEEN_QUERIES)

        with self.dag.lock:
            self.logger.info(
                f'Query for transaction {txn_msg.hash[:10]}...{txn_msg.hash[-10:]} complete')
            self.dag.transactions[txn_msg.hash].queried = True

    def start_collect_metrics(self):
        metrics_not_started = not self.collect_metrics and not self.metrics_end

        if metrics_not_started:
            self.collect_metrics = True
            self.metrics_start = time.time()
            self.metrics_end = self.metrics_start + params.METRICS_DURATION

    def add_peer(self, new_peer):
        addr, port = new_peer
        self.peers.add(new_peer)
        self.logger.info(f'Added new peer {addr}:{port}')
        peers = self.peers.get()

        peer_len = len(peers)
        print('PeerLen:', peer_len, ', Target:', params.PEERS_COUNT-1)
        if peer_len >= params.PEERS_COUNT - 1:
            with self.metrics_lock:
                self.start_collect_metrics()

        if self.analytics_enabled:
            if self.analytics_doc_id is None:
                self.analytics_doc_id = analytics.set_nodes(peers)
                self.logger.info(
                    f'Added to analytics/nodes/{self.analytics_doc_id}')
            else:
                analytics.update_nodes(self.analytics_doc_id, peers)
                self.logger.info(
                    f'Updated analytics/nodes/{self.analytics_doc_id}')

    def send_message(self, node, msg, path='/'):
        start = time.time()
        result = exponential_backoff(
            self.logger, self._send_message, (node, msg, path))

        # failure to send a message to node should remove the peer from the peers list
        # however, the send_message could also originate from the client apps
        if isinstance(result, Exception):
            if not self.is_light_client:
                if node in self.peers:
                    self.peers.remove(node)
            addr, port = node
            self.logger.debug(
                f'Removed peer {addr}:{port} due to inability to respond')
            return
        end = time.time()
        # print(f'send_message took {end-start} seconds')
        return result

    def _send_message(self, node, msg, path):
        session = self.sessions.get(node)
        if not session:
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/octet-stream'})
            self.sessions[node] = session

        host, port = node
        uri = f'http://{host}:{port}{path}'
        req = session.post(uri, data=msg)
        return req.content

    def request_transaction(self, txn_hash, fulfiller_host, fulfiller_port):
        request_sync_msg = messages_pb2.RequestSyncGraph()
        request_sync_msg.address = self.host
        request_sync_msg.port = self.port
        request_sync_msg.pubkey = self.keypair.pubkey.to_string().hex()
        request_sync_msg.target_txn_hash = txn_hash

        try:
            msg = MessageClient.create_message(
                messages_pb2.REQUEST_SYNC_GRAPH_MESSAGE, request_sync_msg)
            node = (fulfiller_host, fulfiller_port)
            response = self.send_message(node, msg)

            common_msg = messages_pb2.CommonMessage()
            common_msg.ParseFromString(response)
            sync_graph = messages_pb2.SyncGraph()
            sync_graph.CopyFrom(common_msg.sync_graph)
            # only the requested transaction should be returned
            if len(sync_graph.transactions) != 1:
                raise ValueError('Expected only 1 transaction')

            txn = sync_graph.transactions[0]
            if txn.hash != txn_hash:
                raise ValueError(f'Wrong transaction hash {txn.hash}')
            return txn
        except Exception as e:
            self.logger.error(e)
            return None

    def receive_transaction(self, txn_msg):
        # valid_txn = self.verify_transaction(txn_msg)
        # if not valid_txn:
        #     self.logger.error(
        #         'Invalid transaction, signature is invalid for '+str(txn_msg))
        #     return

        # dont accept or query transactions that have work done before
        existing_txn = self.dag.transactions.get(txn_msg.hash)
        if not existing_txn:
            with self.dag.lock:
                # self.dag.receive_transaction(txn_msg)
                self.tx_executor.submit(self.dag.receive_transaction, txn_msg)

            self.txn_insert_times[txn_msg.hash] = time.time()
            self.update_metrics(txn_msg)
            # first_level_breadth, max_depth, txn_len = self.dag.analyze_graph()
            # self.logger.info(
            #     f'Graph status (FirstLevelBreadth: {first_level_breadth}, MaxDepth: {max_depth}, TxnLen: {txn_len})')

        if self.analytics_enabled:
            is_preferred = False

            with self.dag.lock:
                conflict_set = set(
                    self.dag.conflicts.get_conflict(txn_msg.hash))
                if conflict_set:
                    is_preferred = self.dag.conflicts.is_preferred(
                        txn_msg.hash)
                    conflict_set.remove(txn_msg.hash)  # remove self

            analytics.set_transaction(
                self.analytics_doc_id, txn_msg, list(conflict_set), is_preferred)
            self.logger.info(f'Added txn {txn_msg.hash[:20]}... to analytics')

    def update_metrics(self, txn_msg):
        current_time = time.time()

        if self.collect_metrics:
            if current_time >= self.metrics_start and current_time < self.metrics_end:
                with self.metrics_lock:
                    if not self.transactions_count:
                        self.logger.info('METRICS_START')
                    self.transactions_count += 1
            elif current_time >= self.metrics_end:
                with self.metrics_lock:
                    self.collect_metrics = False
                    tps = self.transactions_count / params.METRICS_DURATION
                    self.logger.info(
                        f'METRICS_END: {tps} TPS, {self.transactions_count} transactions')

    def broadcast_message(self, msg):
        responses = []
        peers = list(self.peers.get())
        if len(peers) > params.MAX_BROADCAST_PEERS:
            peers = random.sample(peers, params.MAX_BROADCAST_PEERS)

        for addr, port in peers:
            node = (addr, port)
            self.broadcast_executor.submit(self.send_message, node, msg)
            # self.send_message(node, msg)
        # if not peers:
        #     self.logger.info('No peers, did not broadcast transaction')
        return responses

    def sign_transaction(self, txn_msg):
        txn_msg.signature = self.keypair.sign(
            txn_msg.hash.encode('utf-8')).hex()
        return txn_msg

    def verify_transaction(self, txn_msg):
        txn_hash = self.generate_transaction_hash(txn_msg)
        return Keypair.verify(txn_msg.sender_pubkey, txn_msg.signature, txn_hash)

    def generate_transaction_hash(self, txn_msg):
        # Hash of:
        # sender + recipient + amount + nonce + data
        message = txn_msg.sender + txn_msg.recipient + \
            str(txn_msg.amount) + str(txn_msg.nonce) + txn_msg.data
        return sha256(message.encode('utf-8')).hexdigest()

    def generate_txn_object(self, recipient, amount):
        nonce, _ = self.state.send_transaction(self.keypair.address, amount)
        txn_msg = messages_pb2.Transaction()
        txn_msg.sender = self.keypair.address
        txn_msg.recipient = recipient
        txn_msg.amount = amount
        txn_msg.nonce = nonce
        txn_msg.data = ''
        txn_msg.hash = self.generate_transaction_hash(txn_msg)
        txn_msg.sender_pubkey = self.keypair.pubkey.to_string().hex()
        # txn_msg = self.sign_transaction(txn_msg)
        return txn_msg

    def generate_conflicting_txn(self, original_txn_msg, recipient, amount):
        # recompute the transaction hash and signature for conflicting
        txn_msg = messages_pb2.Transaction()
        txn_msg.CopyFrom(original_txn_msg)
        txn_msg.recipient = recipient
        txn_msg.amount = amount
        txn_msg.hash = self.generate_transaction_hash(txn_msg)
        txn_msg = self.sign_transaction(txn_msg)
        return txn_msg

    def generate_transaction(self, recipient, amount):
        txn_msg = self.generate_txn_object(recipient, amount)
        msg = MessageClient.create_message(
            messages_pb2.TRANSACTION_MESSAGE, txn_msg)
        return msg
