from threading import RLock
from utils import read_genesis_state


class StateDB:
    def __init__(self):
        self.balances = {}
        self.nonces = {}
        self.lock = RLock()
        self.load_init_state()

    def load_init_state(self):
        init_state = read_genesis_state()
        for account in init_state:
            address = account['address']
            self.balances[address] = account['balance']
            self.nonces[address] = account['nonce']

    def get_all_addresses(self):
        return list(self.balances.keys())

    def send_transaction(self, sender, amount):
        updated_nonce = None
        updated_balance = None
        with self.lock:
            self.nonces[sender] += 1
            self.balances[sender] -= amount
            updated_nonce = self.nonces[sender]
            updated_balance = self.balances[sender]
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
