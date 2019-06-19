import config
import time
from src.crypto import Keypair
from src.message_client import MessageClient
from src.proto import messages_pb2


def test_bootstrap_state():
    client = MessageClient(light_client=True)
    recipient = Keypair()
    attacker = Keypair()
    entries = 5

    messages = [client.generate_txn_object(
        recipient.address, 100) for _ in range(entries)]
    conflict_messages = [client.generate_conflicting_txn(
        msg, attacker.address, 100) for msg in messages]
    all_messages = messages + conflict_messages
    conflict_sets = zip(messages, conflict_messages)
    conflict_sets = [(m.hash, c.hash) for m, c in conflict_sets]

    sync_graph_msg = messages_pb2.SyncGraph()
    sync_graph_msg.transactions.extend(all_messages)

    for conflict_set in conflict_sets:
        conflict_msg = messages_pb2.ConflictSet()
        conflict_msg.hashes.extend(conflict_set)
        sync_graph_msg.conflicts.append(conflict_msg)

    client.bootstrap_graph(sync_graph_msg)

    assert len(client.dag.transactions) == len(all_messages)
    for msg in all_messages:
        assert msg.hash in client.dag.transactions
        assert client.dag.transactions.get(msg.hash) == msg

    for conflict_set in conflict_sets:
        for txn_hash in conflict_set:
            assert client.dag.conflicts.get_conflict(txn_hash)
            assert client.dag.conflicts.get_preferred(txn_hash)


def test_median_acceptance():
    client = MessageClient(light_client=True)
    recipient = Keypair()
    client.start_collect_metrics()

    entries = 5
    messages = [client.generate_txn_object(
        recipient.address, 100) for _ in range(entries)]

    for msg in messages:
        client.receive_transaction(msg)

    # transactions not accepted yet
    median, total = client.calculate_median_acceptance_times()
    assert median == 0
    assert total == 0

    for msg in messages:
        client.dag.transactions[msg.hash].accepted = True
        client.txn_accepted_times[msg.hash] = time.time()

    median, total = client.calculate_median_acceptance_times()
    assert median > 0
    assert total == entries
