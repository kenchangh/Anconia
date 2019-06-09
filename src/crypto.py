import random
from hashlib import sha256
from ecdsa import SigningKey, NIST192p


class Keypair:
    def __init__(self):
        self.privkey = SigningKey.generate()  # uses NIST192p
        self.pubkey = self.privkey.get_verifying_key()
        self.address = Keypair.generate_address(self.pubkey)

    @staticmethod
    def generate_address(pubkey):
        # we follow Ethereum's address format generation
        # take the hash(public_key) and only use the last 20 characters
        address = sha256(pubkey.to_string()).hexdigest()[-20:]
        return address

    @staticmethod
    def from_genesis_file(accounts):
        account = random.choice(accounts)
        keypair = Keypair()
        privkey = bytes.fromhex(account['privkey'])
        privkey = SigningKey.from_string(privkey, curve=NIST192p)

        keypair.privkey = privkey
        keypair.pubkey = privkey.get_verifying_key()
        keypair.address = Keypair.generate_address(keypair.pubkey)
        return keypair

    def sign(self, message):
        signature = self.privkey.sign(message)
        return signature

    def verify(self, signature, message):
        return self.pubkey.verify(signature, message)
