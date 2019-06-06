from hashlib import sha256
from ecdsa import SigningKey


class Keypair:
    def __init__(self):
        self.privkey = SigningKey.generate()  # uses NIST192p
        self.pubkey = self.privkey.get_verifying_key()
        self.address = sha256(self.privkey).hexdigest()

    def sign(self, message):
        signature = self.privkey.sign(message)
        return signature

    def verify(self, signature, message):
        return self.pubkey.verify(signature, message)
