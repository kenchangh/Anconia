from threading import RLock, Lock
import json
import time
from google.protobuf.json_format import MessageToDict


class ConflictSet:
    def __init__(self):
        self.lookup = {}
        self.conflicts = []
        self.preferred = {}
        self.lock = RLock()

    def add_conflict(self, *txns):
        # conflicts are transitive,
        # so when a txn_hash already exists in the conflict lookup table
        # just add the other conflicting transactions into the conflict set
        with self.lock:
            conflict_index = None
            for txn_hash in txns:
                conflict_index = self.lookup.get(txn_hash)
                if conflict_index is not None:
                    for txn_hash in txns:
                        self.lookup[txn_hash] = conflict_index
                        self.conflicts[conflict_index].add(txn_hash)
                    return self.conflicts[conflict_index]

            if not conflict_index:
                conflict_set = set(txns)
                self.conflicts.append(conflict_set)
                conflict_index = len(self.conflicts) - 1

                for txn_hash in txns:
                    self.lookup[txn_hash] = conflict_index
                return conflict_set

    def get_conflict(self, txn_hash):
        conflict_index = None
        with self.lock:
            conflict_index = self.lookup.get(txn_hash, None)
            if conflict_index is None:
                return set([])
            return self.conflicts[conflict_index]

    def set_preferred(self, txn_hash):
        with self.lock:
            conflict_index = self.lookup.get(txn_hash, None)
            if conflict_index is None:
                raise ValueError(f"No conflict set for {txn_hash}")
            self.preferred[conflict_index] = txn_hash

    def is_preferred(self, txn_hash):
        with self.lock:
            conflict_index = self.lookup.get(txn_hash, None)
            if conflict_index is None:
                raise ValueError(f"No conflict set for {txn_hash}")
            return self.preferred.get(conflict_index) == txn_hash


class DAG:
    def __init__(self):
        self.transactions = {}
        self.conflicts = ConflictSet()
        self.lock = RLock()

    def update_chit(self, txn_hash, chit):
        with self.lock:
            self.transactions[txn_hash].chit = chit

    def check_for_conflict(self, incoming_txn):
        conflict = set([])
        for txn_hash in self.transactions:
            txn = self.transactions[txn_hash]
            if txn.sender == incoming_txn.sender and txn.nonce == incoming_txn.nonce:
                updated_conflict = set([])
                updated_conflict = self.conflicts.add_conflict(
                    incoming_txn.hash, txn.hash)
                return updated_conflict
        return conflict

    def receive_transaction(self, incoming_txn):
        with self.lock:
            if not self.transactions.get(incoming_txn.hash):
                self.check_for_conflict(incoming_txn)
                parents = self.select_parents(incoming_txn)
                incoming_txn.parents.extend(parents)
                for parent in parents:
                    self.transactions[parent].children.append(
                        incoming_txn.hash)

                incoming_txn.chit = False
                self.transactions[incoming_txn.hash] = incoming_txn

    def select_parents(self, incoming_txn):
        # to select a parent, we select a transaction
        # which itself and its progeny do not have conflicts
        # and with the highest confidence

        # we do it with a retreating search
        # search from the frontier, towards the genesis vertex
        eligible_parents = []

        for txn_hash in reversed(tuple(self.transactions.keys())):
            # early termination
            if len(eligible_parents) >= 30:
                break
            txn = self.transactions[txn_hash]
            # if self.is_strongly_preferred(txn):
            n_conflicts = len(self.conflicts.get_conflict(txn_hash))
            confidence = self.confidence(txn)
            if confidence > 0 or n_conflicts == 0:
                eligible_parents.append(txn_hash)

        return eligible_parents

    def confidence(self, txn):
        visited = {}
        queue = []
        confidence = 0
        queue.append(txn.hash)
        visited[txn.hash] = True

        while queue:
            txn_hash = queue.pop(0)
            txn = self.transactions[txn_hash]
            for child in txn.children:
                confidence += self.transactions[child].chit
                if not visited.get(child):
                    queue.append(child)
                    visited[child] = True
        return confidence

    def is_strongly_preferred(self, txn):
        visited = {}
        queue = []
        queue.append(txn.hash)
        visited[txn.hash] = True

        while queue:
            txn_hash = queue.pop(0)
            if not self.conflicts.is_preferred(txn_hash):
                return False
            parents = self.transactions[txn_hash].parents
            for parent in parents:
                if not visited.get(parent):
                    queue.append(parent)
                    visited[parent] = True
        return True
