import random
from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey, NIST192p


class Keypair:
    def __init__(self):
        self.privkey = SigningKey.generate()  # uses NIST192p
        self.pubkey = self.privkey.get_verifying_key()
        self.address = Keypair.generate_address(self.pubkey)
        self.nice_address = 'anc'+self.address

    @staticmethod
    def generate_address(pubkey):
        # we follow Ethereum's address format generation
        # take the hash(public_key) and only use the last 20 characters
        address = sha256(pubkey.to_string()).hexdigest()[-20:]
        return address

    @staticmethod
    def from_private_key(privkey):
        keypair = Keypair()
        keypair.privkey = privkey
        keypair.pubkey = privkey.get_verifying_key()
        keypair.address = Keypair.generate_address(keypair.pubkey)
        keypair.nice_address = 'anc'+keypair.address
        return keypair

    @staticmethod
    def from_genesis_file(accounts):
        account = random.choice(accounts)
        keypair = Keypair()
        privkey = bytes.fromhex(account['privkey'])
        privkey = SigningKey.from_string(privkey, curve=NIST192p)

        keypair.privkey = privkey
        keypair.pubkey = privkey.get_verifying_key()
        keypair.address = Keypair.generate_address(keypair.pubkey)
        keypair.nice_address = 'anc'+keypair.address
        return keypair

    def sign(self, message):
        signature = self.privkey.sign(message)
        return signature

    @staticmethod
    def verify(pubkey, signature, message):
        pubkey = bytes.fromhex(pubkey)
        pubkey = VerifyingKey.from_string(pubkey, curve=NIST192p)
        signature = bytes.fromhex(signature)
        return pubkey.verify(signature, message.encode('utf-8'))
