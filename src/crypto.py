from hashlib import sha256
from ecdsa import SigningKey


class Keypair:
    def __init__(self):
        self.privkey = SigningKey.generate()  # uses NIST192p
        self.pubkey = self.privkey.get_verifying_key()
        # we follow Ethereum's address format generation
        # take the hash(public_key) and only use the last 20 characters
        self.address = sha256(self.pubkey.to_string()).hexdigest()[-20:]

    def sign(self, message):
        signature = self.privkey.sign(message)
        return signature

    def verify(self, signature, message):
        return self.pubkey.verify(signature, message)
