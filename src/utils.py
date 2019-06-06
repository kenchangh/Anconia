import json
from ecdsa import SigningKey


def generate_init_state(n=50, init_amount=1000000):
    accounts = []
    for i in range(n):
        privkey = SigningKey.generate()
        account = {
            'privkey': privkey.to_string().hex(),
            'balance': init_amount,
            'nonce': 0
        }
        accounts.append(account)
    return json.dumps(accounts)


if __name__ == "__main__":
    print(generate_init_state())
