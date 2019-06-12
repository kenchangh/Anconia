import config
import time
import pytest
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

    entries = 5
    messages = []
    conflicting_messages = []

    for _ in range(entries):
        msg = client.generate_txn_object(recipient.address, 100)
        dag.receive_transaction(msg)
        with pytest.raises(ValueError):
            dag.conflicts.set_preferred(msg.hash)
        messages.append(msg)

    for msg in messages:
        conflict_msg = client.generate_conflicting_txn(
            msg, attacker.address, 100)
        dag.receive_transaction(conflict_msg)
        dag.conflicts.set_preferred(msg.hash)
        conflicting_messages.append(conflict_msg)

    conflict_sets = [set([m[0].hash, m[1].hash])
                     for m in zip(messages, conflicting_messages)]

    assert len(dag.conflicts.conflicts) == len(conflict_sets)
    assert len(dag.transactions) == len(messages) + len(conflicting_messages)
    txn_hashes = list(dag.transactions.keys())

    for msg_hash, conflict_msg_hash in conflict_sets:
        assert msg_hash in txn_hashes
        assert conflict_msg_hash in txn_hashes

    for msg in messages:
        assert dag.conflicts.is_preferred(msg.hash)


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
    conflicting_messages = []

    for _ in range(entries):
        msg = client.generate_txn_object(recipient.address, 100)
        dag.receive_transaction(msg)
        messages.append(msg)

    for msg in messages:
        conflict_msg = client.generate_conflicting_txn(
            msg, attacker.address, 100)
        dag.receive_transaction(conflict_msg)
        dag.conflicts.set_preferred(msg.hash)

    all_messages = zip(messages, conflicting_messages)

    for msg, conflict_msg in all_messages:
        assert dag.is_strongly_preferred(msg)
        assert not dag.is_strongly_preferred(conflict_msg)
