import socket
import time
import math
import logging
import random
from hashlib import sha256
from threading import Lock
from proto import messages_pb2
from common import exponential_backoff
from utils import read_genesis_state
from crypto import Keypair
from statedb import StateDB
from dag import DAG
import params

# TO BE UPDATED PERIODICALLY
ATTR_NAMES = {
    messages_pb2.NODE_QUERY_MESSAGE: 'node_query',
    messages_pb2.JOIN_MESSAGE: 'join',
    messages_pb2.TRANSACTION_MESSAGE: 'transaction',
}


class MessageClient:
    def __init__(self, light_client=False):
        """
        Client that interacts with other peers in the network.

        light_client=True, to disable peering and storing peer information.
        """
        self.state = StateDB()
        self.keypair = Keypair.from_genesis_file(read_genesis_state())
        self.dag = DAG()
        self.peers = set([])

        self.logger = logging.getLogger('main')
        self.is_light_client = light_client
        self.lock = Lock()

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

    def query_txn(self, txn_msg):
        query_nodes = []
        query_success_threshold = math.floor(
            params.ALPHA_PARAM * params.NETWORK_SAMPLE_SIZE)
        strongly_preferred_count = 0
        short_txn_hash = txn_msg.hash[:20]

        with self.lock:
            if len(self.peers) < params.NETWORK_SAMPLE_SIZE:
                query_nodes = list(self.peers)
            else:
                query_nodes = random.sample(
                    self.peers, params.NETWORK_SAMPLE_SIZE)

        start_time = time.time()
        end_by_time = start_time + params.QUERY_TIMEOUT

        for node in query_nodes:
            # exceeded QUERY_TIMEOUT
            if time.time() >= end_by_time:
                self.logger.debug(f'Timeout for query of {short_txn_hash}...')
                break
            node_query = messages_pb2.NodeQuery()
            node_query.txn_hash = txn_msg.hash
            is_strongly_preferred = self.dag.is_strongly_preferred(txn_msg)
            node_query.is_strongly_preferred = is_strongly_preferred
            msg = MessageClient.create_message(
                messages_pb2.NODE_QUERY_MESSAGE, node_query)

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

        self.logger.debug(
            f'Received {strongly_preferred_count} strongly-preferred responses')

        if strongly_preferred_count >= query_success_threshold:
            with self.dag.lock:
                short_txn_hash = txn_msg.hash[:20]
                self.logger.debug(f'Added chit to {short_txn_hash}...')
                self.dag.transactions[txn_msg.hash].chit = True

    def add_peer(self, new_peer):
        addr, port = new_peer
        self.peers.add(new_peer)
        self.logger.info(f'Added new peer {addr}:{port}')

    def send_message(self, node, msg):
        result = exponential_backoff(
            self.logger, self._send_message, (node, msg))

        # failure to send a message to node should remove the peer from the peers list
        # however, the send_message could also originate from the client apps
        if isinstance(result, Exception):
            if not self.is_light_client:
                self.peers.remove(node)
            addr, port = node
            self.logger.debug(
                f'Removed peer {addr}:{port} due to inability to respond')
            return
        return result

    def _send_message(self, node, msg):
        addr, port = node
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.logger.debug(f'Connecting to {addr}:{port}')
        s.connect((addr, port))
        s.sendall(msg)
        data = s.recv(1024)

        return data

    def receive_transaction(self, txn_msg):
        self.dag.receive_transaction(txn_msg)
        self.query_txn(txn_msg)

    def broadcast_message(self, msg):
        responses = []
        peers = set(self.peers)
        for addr, port in peers:
            node = (addr, port)
            self.send_message(node, msg)
        if peers:
            self.logger.info('Broadcasted transaction')
        else:
            self.logger.info('No peers, did not broadcast transaction')
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
        txn_msg = self.sign_transaction(txn_msg)
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
