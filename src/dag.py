from threading import RLock, Lock
import json
import time
import logging
import params
from google.protobuf.json_format import MessageToDict


class ConflictSet:
    def __init__(self):
        self.lookup = {}
        self.conflicts = []
        self.preferred = {}
        self.lock = RLock()
        self.logger = logging.getLogger('main')

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

    def get_preferred(self, txn_hash):
        with self.lock:
            conflict_index = self.lookup.get(txn_hash, None)
            if conflict_index is None:
                raise ValueError(f"No conflict set for {txn_hash}")
            return self.preferred.get(conflict_index)

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
                self.conflicts.add_conflict(
                    incoming_txn.hash, txn.hash)
                preferred = self.decide_on_preference(incoming_txn.hash)
                # print(
                #     f'Conflict exists! ({txn.hash[:20]}, {incoming_txn.hash[:20]})')
                # print(f'Preferred txn {preferred[:20]}')
        return conflict

    def receive_transaction(self, incoming_txn):
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
            if len(eligible_parents) >= params.MAX_PARENTS:
                break
            txn = self.transactions[txn_hash]
            # if self.is_strongly_preferred(txn):
            # n_conflicts = len(self.conflicts.get_conflict(txn_hash))

            if self.is_strongly_preferred(txn):
                progeny_has_conflict = self.progeny_has_conflict(txn)
                confidence = self.confidence(txn)
                if confidence > 0 or not progeny_has_conflict:
                    # if not progeny_has_conflict:
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
                child_txn = self.transactions.get(child)
                if child_txn:
                    confidence += child_txn.chit
                if not visited.get(child):
                    queue.append(child)
                    visited[child] = True
        return confidence

    def decide_on_preference(self, txn_hash):
        # sorting the conflict set ensures that all nodes
        # converge on the same order for preferring certain transactions
        # in the event of transactions having the same confidence
        conflict_set = sorted(list(self.conflicts.get_conflict(txn_hash)))
        confidences = []

        for conflict_hash in conflict_set:
            txn = self.transactions.get(conflict_hash)
            # if txn does not exist, we should request it with MessageClient
            # but we leave that for another day
            if not txn:
                continue
            confidence = self.confidence(txn)
            confidences.append(confidence)
        txn_index = confidences.index(max(confidences))
        preferred = conflict_set[txn_index]

        self.conflicts.set_preferred(preferred)
        return preferred

    def progeny_has_conflict(self, txn):
        visited = {}
        queue = []
        queue.append(txn.hash)
        visited[txn.hash] = True

        while queue:
            txn_hash = queue.pop(0)
            txn = self.transactions[txn_hash]
            conflicts = self.conflicts.get_conflict(txn_hash)
            if conflicts:
                return True

            for child in txn.children:
                if not visited.get(child):
                    queue.append(child)
                    visited[child] = True
        return False

    def is_strongly_preferred(self, txn):
        visited = {}
        queue = []
        queue.append(txn.hash)
        visited[txn.hash] = True

        while queue:
            txn_hash = queue.pop(0)
            conflict_set = self.conflicts.get_conflict(txn_hash)

            # if there is no current preference the conflict set of txn_hash,
            # decide with the transaction that has the highest confidence
            # if both have the same confidence, prefer the one that came sooner
            if conflict_set:
                preferred = self.conflicts.get_preferred(txn_hash)

                if preferred is None:
                    self.decide_on_preference(txn_hash)
                elif preferred != txn_hash:
                    return False

            parents = self.transactions[txn_hash].parents
            for parent in parents:
                if not visited.get(parent):
                    queue.append(parent)
                    visited[parent] = True
        return True

    def update_accepted(self, txn):
        # check the ancestor of the txn if
        # it has enough confidence
        visited = {}
        queue = []
        queue.append(txn.hash)
        visited[txn.hash] = True

        while queue:
            txn_hash = queue.pop(0)
            txn = self.transactions[txn_hash]

            if txn.queried and txn.chit:
                if not txn.accepted:
                    confidence = self.confidence(txn)
                    if confidence > params.BETA_CONFIDENCE_PARAM:
                        with self.lock:
                            self.transactions[txn_hash].accepted = True
                    else:
                        return False
            else:
                return False

            parents = txn.parents
            for parent in parents:
                if not visited.get(parent):
                    queue.append(parent)
                    visited[parent] = True
        return True

    def analyze_graph(self):
        max_depth = 0
        max_breadth = 0
        keys = self.transactions.keys()
        genesis_nodes = []

        for txn_hash in keys:
            txn = self.transactions[txn_hash]
            if len(txn.parents) == 0:
                max_breadth += 1
                genesis_nodes.append(txn_hash)

        max_depths = [self.DFS(node) for node in genesis_nodes]
        max_depth = max(max_depths)
        return max_breadth, max_depth, len(keys)

    def DFS(self, s):
        visited = {}
        stack = []
        stack.append(s)
        max_depth = 0

        while len(stack):
            if len(stack) > max_depth:
                max_depth = len(stack)

            # Pop a vertex from stack and print it
            s = stack[-1]
            stack.pop()

            # Stack may contain same vertex twice. So
            # we need to print the popped item only
            # if it is not visited.
            if not visited.get(s):
                visited[s] = True

            # Get all adjacent vertices of the popped vertex s
            # If a adjacent has not been visited, then puah it
            # to the stack.
            children = self.transactions[s].children
            for node in children:
                if not visited.get(node):
                    stack.append(node)

        return max_depth
