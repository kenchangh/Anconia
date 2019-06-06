import json
import os
from hashlib import sha256
from crypto import Keypair


def generate_init_state(n=500, init_amount=1000000):
    accounts = []
    for _ in range(n):
        keypair = Keypair()
        str_priv_key = keypair.privkey.to_string()
        account = {
            'privkey': str_priv_key.hex(),
            'address': keypair.address,
            'balance': init_amount,
            'nonce': 0
        }
        accounts.append(account)
    return json.dumps(accounts)


def read_genesis_state():
    src_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(src_dir)
    init_json = os.path.join(root_dir, 'data', 'genesis.json')
    with open(init_json) as f:
        return json.load(f)


if __name__ == "__main__":
    print(generate_init_state())
    # read_init_state()
