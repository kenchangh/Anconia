
class DAG:
    def __init__(self):
        self.chits = {}
        self.transactions = {}
        self.queried = {}
        self.conflicts = {}

    def check_for_conflict(self, incoming_txn):
        conflict = False
        for txn_hash in self.transactions:
            txn = self.transactions[txn_hash]
            if txn.sender == incoming_txn.sender and txn.nonce == incoming_txn.nonce:
                conflict_set = (incoming_txn.hash, txn.hash)
                self.conflicts[conflict_set] = (incoming_txn, txn)
                conflict = True
                print(self.conflicts)
        return conflict

    def receive_transaction(self, incoming_txn):
        if not self.transactions.get(incoming_txn.hash):
            self.transactions[incoming_txn.hash] = incoming_txn
            self.check_for_conflict(incoming_txn)
