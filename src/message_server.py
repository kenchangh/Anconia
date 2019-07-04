import sys
import socket
import struct
import asyncio
import time
import params
import binascii
from threading import Thread
import logging
from concurrent.futures import ThreadPoolExecutor
import socketserver
import traceback
from japronto import Application
from proto import messages_pb2
from message_client import MessageClient
from common import exponential_backoff, simulate_network_latency


class MessageServer:
    def __init__(self, message_client, host=None, port=None):
        self.message_client = message_client
        self.sock = None
        self.logger = logging.getLogger('main')
        self.address = host
        self.port = port
        self.listener_thread = None
        # self.thread_executor = ThreadPoolExecutor(max_workers=8)

    def start(self):
        self.init_self()
        app = Application()
        app.router.add_route('/init', self.init_server, methods=['POST'])
        app.router.add_route('/balance', self.check_balance, methods=['POST'])
        app.router.add_route(
            '/txstatus', self.check_txstatus, methods=['POST'])
        app.router.add_route('/', self.handle_message, methods=['POST'])
        app.run(host=self.address, port=self.port)
        return self.address, self.port

    def init_self(self):
        def _init_self():
            time.sleep(params.INIT_SERVER_DELAY)
            self.message_client.send_message(
                (self.address, self.port), b'', '/init')
        thread = Thread(target=_init_self)
        thread.start()

    def init_server(self, request):
        self.message_client.sync_graph()
        self.message_client.start_query_worker()
        return request.Response(body=b'')

    def check_txstatus(self, request):
        request_tx = messages_pb2.RequestTransaction()
        request_tx.ParseFromString(request.body)
        txn = self.message_client.dag.transactions[request_tx.hash]
        msg = txn.SerializeToString()
        return request.Response(body=msg)

    def check_balance(self, request):
        check_balance = messages_pb2.CheckBalance()
        check_balance.ParseFromString(request.body)

        if len(check_balance.address) != 23:
            return request.Response(code=400)
        address = check_balance.address[3:]

        balance = self.message_client.state.balances.get(address, 0)
        nonce = self.message_client.state.nonces.get(address, 0)
        balance_response = messages_pb2.BalanceResponse()
        balance_response.address = check_balance.address
        balance_response.balance = balance
        balance_response.nonce = nonce
        msg = balance_response.SerializeToString()

        return request.Response(body=msg)

    def handle_message(self, request):
        raw_msg = request.body
        try:
            common_msg = messages_pb2.CommonMessage()
            common_msg.ParseFromString(raw_msg)

            message_handlers = {
                messages_pb2.JOIN_MESSAGE: ('Join', 'join', self.add_peer),
                messages_pb2.TRANSACTION_MESSAGE: ('Transaction', 'transaction', self.handle_transaction),
                messages_pb2.NODE_QUERY_MESSAGE: (
                    'NodeQuery', 'node_query', self.handle_node_query),
                messages_pb2.REQUEST_SYNC_GRAPH_MESSAGE: (
                    'RequestSyncGraph', 'request_sync_graph', self.handle_sync_graph),
                messages_pb2.BATCH_TRANSACTIONS_MESSAGE: (
                    'BatchTransactions', 'batch_transactions', self.handle_batch_transactions),
            }

            handler = message_handlers.get(common_msg.message_type)
            if not handler:
                raise ValueError(
                    f"There is no message type {common_msg.message_type} or handler not created yet")

            message_classname, attr_name, handler_function = handler
            sub_msg = getattr(messages_pb2, message_classname)()
            sub_msg.CopyFrom(getattr(common_msg, attr_name))
            return handler_function(request, sub_msg)
        except Exception:
            traceback.print_exc()
            return request.Response(code=500)
        return request.Response(body=b'')

    def handle_transaction(self, request, txn_msg):
        self.message_client.receive_transaction(txn_msg)
        return request.Response(body=b'')

    def handle_batch_transactions(self, request, batch_txns_msg):
        # print('received batch')
        for txn_msg in batch_txns_msg.transactions:
            self.message_client.receive_transaction(txn_msg)

        return request.Response(body=b'')

    def handle_node_query(self, request, query_msg):
        """
        If we have not encountered the transaction yet,
        Respond the query with the query's is_strongly_preferred field
        And store the transaction into our own DAG.

        If encountered before, respond with own preference.
        """
        txn_hash = query_msg.txn_hash
        is_strongly_preferred = False

        with self.message_client.lock:
            if not self.message_client.dag.transactions.get(txn_hash):
                # if transaction doesn't exist locally,
                # request from the querying node to patch the transaction
                # make own decision from received transaction
                # txn = self.message_client.request_transaction(
                #     txn_hash, query_msg.from_address, query_msg.from_port)
                # if txn:
                #     self.message_client.receive_transaction(txn)
                #     is_strongly_preferred = self.message_client.dag.is_strongly_preferred(
                #         txn)
                # else:
                #     is_strongly_preferred = query_msg.is_strongly_preferred
                is_strongly_preferred = query_msg.is_strongly_preferred
            else:
                txn = self.message_client.dag.transactions[txn_hash]
                is_strongly_preferred = self.message_client.dag.is_strongly_preferred(
                    txn)
                # print(
                #     f'Default: {query_msg.is_strongly_preferred}, Response: {is_strongly_preferred}')

        response_query = messages_pb2.NodeQuery()
        response_query.txn_hash = txn_hash
        response_query.is_strongly_preferred = is_strongly_preferred
        response_query.from_address = self.address
        response_query.from_port = self.port
        msg = MessageClient.create_message(
            messages_pb2.NODE_QUERY_MESSAGE, response_query)
        return request.Response(body=msg)

    def handle_sync_graph(self, request, request_sync_graph_msg):
        if request_sync_graph_msg.target_txn_hash:
            sync_msg = messages_pb2.SyncGraph()
            txn = self.message_client.dag.transactions.get(
                request_sync_graph_msg.target_txn_hash)

            if txn:
                sync_msg.transactions.append(txn)
                msg = MessageClient.create_message(
                    messages_pb2.SYNC_GRAPH_MESSAGE, sync_msg)
                return request.Response(body=msg)
            return request.Response(body=msg)

        sync_msg = messages_pb2.SyncGraph()
        transactions = self.message_client.dag.transactions.values()
        sync_msg.transactions.extend(transactions)
        conflict_sets = self.message_client.dag.conflicts.conflicts

        for conflict_set in conflict_sets:
            conflict_msg = messages_pb2.ConflictSet()
            conflict_msg.hashes.extend(conflict_set)
            sync_msg.conflicts.append(conflict_msg)

        msg = MessageClient.create_message(
            messages_pb2.SYNC_GRAPH_MESSAGE, sync_msg
        )
        return request.Response(body=msg)

    def add_peer(self, request, join_msg):
        new_peer = (join_msg.address, join_msg.port)
        with self.message_client.lock:
            self.message_client.add_peer(new_peer)
        return request.Response(body=b'')
