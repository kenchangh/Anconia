import config
import time
from src.consensus import consensus_algorithm
from src.crypto import Keypair
from src.message_client import MessageClient
from src.dag import ConflictSet, DAG


def test_conflict_set():
    conflict_sets = ConflictSet()
    conflicts = [1, 2, 3]
    assert conflict_sets.get_conflict(conflicts[0]) == set([])
    updated_conflicts = conflict_sets.add_conflict(*conflicts)
    assert updated_conflicts == set(conflicts)
    for tx in conflicts:
        assert conflict_sets.get_conflict(tx) == set(conflicts)

    new_conflicts = [1, 4]
    updated_conflicts = conflict_sets.add_conflict(*new_conflicts)
    for tx in new_conflicts:
        assert conflict_sets.get_conflict(tx) == set(
            conflicts).union(set(new_conflicts))


def test_dag_conflicts():
    dag = DAG()
    client = MessageClient(
        consensus_algorithm=consensus_algorithm, light_client=True)
    recipient = Keypair()
    attacker = Keypair()

    msg = client.generate_txn_object(recipient.address, 100)
    assert client.verify_transaction(msg)

    dag.receive_transaction(msg)
    conflict_msg = client.generate_conflicting_txn(msg, attacker.address, 100)
    dag.receive_transaction(conflict_msg)

    conflict_set = set([msg.hash, conflict_msg.hash])
    assert len(dag.conflicts.conflicts) == 1
    assert dag.conflicts.conflicts[0] == conflict_set
    assert len(dag.transactions) == 2

    txn_hashes = list(dag.transactions.keys())
    assert msg.hash in txn_hashes
    assert conflict_msg.hash in txn_hashes


def confidence(n):
    if n == 0:
        return 0
    else:
        return n + confidence(n-1)


def test_dag_confidence():
    dag = DAG()
    client = MessageClient(
        consensus_algorithm=consensus_algorithm, light_client=True)
    recipient = Keypair()
    entries = 5
    for _ in range(entries):
        msg = client.generate_txn_object(recipient.address, 100)
        dag.receive_transaction(msg)
        dag.update_chit(msg.hash, True)

    for txn_hash in dag.transactions:
        txn = dag.transactions[txn_hash]
        assert dag.confidence(txn) == confidence(len(txn.children))


def test_dag_strongly_preferred():
    dag = DAG()
    client = MessageClient(
        consensus_algorithm=consensus_algorithm, light_client=True)
    recipient = Keypair()
    attacker = Keypair()
    entries = 5
    messages = []

    for _ in range(entries):
        msg = client.generate_txn_object(recipient.address, 100)
        dag.receive_transaction(msg)
        dag.update_chit(msg.hash, True)
        # dag.conflicts.set_preferred(msg.hash)
        messages.append(msg)

    for msg in messages:
        conflict_msg = client.generate_conflicting_txn(
            msg, attacker.address, 100)
        dag.receive_transaction(conflict_msg)

    print(dag.transactions)
    print(dag.conflicts.conflicts)
    assert 0
