import socket
import time
import logging
from hashlib import sha256
from threading import Lock
from proto import messages_pb2
from common import exponential_backoff
from utils import read_genesis_state
from crypto import Keypair
from statedb import StateDB
from dag import DAG

# TO BE UPDATED PERIODICALLY
ATTR_NAMES = {
    messages_pb2.NODE_QUERY_MESSAGE: 'node_query',
    messages_pb2.JOIN_MESSAGE: 'join',
    messages_pb2.TRANSACTION_MESSAGE: 'transaction',
}


class MessageClient:
    def __init__(self, consensus_algorithm, light_client=False):
        self.state = StateDB()
        self.keypair = Keypair.from_genesis_file(read_genesis_state())
        self.dag = DAG()
        self.peers = set([])

        self.consensus_algorithm = consensus_algorithm
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

    def run_consensus(self, txn_msg):
        self.consensus_algorithm(self, txn_msg)

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

    def broadcast_message(self, msg):
        responses = []
        peers = set(self.peers)
        for addr, port in peers:
            node = (addr, port)
            self.send_message(node, msg)
        if self.peers:
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
        txn_msg = self.generate_transaction_object(recipient, amount)
        msg = MessageClient.create_message(
            messages_pb2.TRANSACTION_MESSAGE, txn_msg)
        return msg
