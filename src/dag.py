from threading import RLock


class DAG:
    def __init__(self):
        self.chits = {}
        self.transactions = {}
        self.queried = {}
        self.conflicts = {}
        self.lock = RLock()

    def check_for_conflict(self, incoming_txn):
        conflict = False
        for txn_hash in self.transactions:
            txn = self.transactions[txn_hash]
            if txn.sender == incoming_txn.sender and txn.nonce == incoming_txn.nonce:
                # the dict key-values are doubly linked
                if self.conflicts.get(incoming_txn.hash):
                    self.conflicts[incoming_txn.hash].append(txn.hash)
                else:
                    self.conflicts[incoming_txn.hash] = [txn.hash]

                if self.conflicts.get(txn.hash):
                    self.conflicts[txn.hash].append(incoming_txn.hash)
                else:
                    self.conflicts[txn.hash] = [incoming_txn.hash]
                conflict = True
        return conflict

    def receive_transaction(self, incoming_txn):
        if not self.transactions.get(incoming_txn.hash):
            with self.lock:
                self.check_for_conflict(incoming_txn)
                self.select_parent(incoming_txn)
                self.transactions[incoming_txn.hash] = incoming_txn

    def select_parent(self, incoming_txn):
        # to select a parent, we select a transaction
        # which itself and its progeny do not have conflicts
        # and with the highest confidence

        # we do it with a retreating search
        # search from the frontier, towards the genesis vertex
        eligible_parents = []

        for txn_hash in self.transactions:
            txn = self.transactions[txn_hash]
            if self.is_strongly_preferred(txn):
                n_conflicts = len(self.conflicts.get(txn_hash, []))
                confidence = self.confidence(txn)
                print('Confidence', confidence)
                if confidence > 0 and n_conflicts == 0:
                    eligible_parents.append(txn_hash)

        # for txn_hash in eligible_parents:
        #     parent_txn = self.transactions[txn_hash]

    def confidence(self, txn):
        if len(txn.children) == 0:
            return 0
        else:
            num_child = len(txn.child)
            confidences = [self.confidence(
                self.transactions[child]) for child in txn.child]
            confidence = num_child + sum(confidences)
            return confidence

    def is_strongly_preferred(self, txn):
        return 1
