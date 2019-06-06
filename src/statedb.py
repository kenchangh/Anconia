from threading import RLock


class StateDB:
    def __init__(self, initial_state):
        self.balances = {}
        self.nonces = {}
        self.lock = RLock()

    def send_transaction(self, address, amount):
        updated_nonce = None
        updated_balance = None
        with self.lock:
            self.nonces[address] += 1
            self.balances[address] -= amount
            updated_nonce = self.nonces[address]
            updated_balance = self.balances[address]
        return updated_nonce, updated_balance

    def receive_transaction(self, address, amount):
        updated_balance = None
        with self.lock:
            current_balance = self.balances.get(address)
            if current_balance is None:
                self.balances[address] = amount
            else:
                self.balances[address] += amount
            updated_balance = self.balances[address]
        return updated_balance
