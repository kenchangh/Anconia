from message_client import MessageClient
from crypto import Keypair, SigningKey, NIST192p


def generate_wallet():
    keypair = Keypair()
    print()
    print('Your new wallet address is:', keypair.nice_address)
    print('Please keep your private key safe!')
    print(keypair.privkey.to_string().hex())


def print_account(privkey_input):
    privkey = SigningKey.from_string(privkey_input, curve=NIST192p)
    keypair = Keypair.from_private_key(privkey)
    message_client = MessageClient(light_client=True, own_key=keypair)
    balance_response = message_client.check_balance()

    print()
    print('Address:', balance_response.address)
    print('Balance:', f'{balance_response.balance} ANC')
    print('Nonce:', balance_response.nonce)
    print()


def use_own_wallet():
    print()
    print('Insert your private keys:', end=' ')
    privkey_input = bytes.fromhex(input())
    print_account(privkey_input)


def send_receive_anc():
    print('You can either:')
    print('1. Send ANC to another user')
    print('2. Receive ANC to another user')


def main():
    print('Welcome to Anconia blockchain.')

    while True:
        print('Please select one of the options below:')
        print('1. Generate wallet')
        print('2. Use own wallet')
        print('Input your choice:', end=" ")
        choice = input()

        GENERATE_WALLET = 1
        OWN_WALLET = 2

        try:
            choice = int(choice)
            if choice != 1 and choice != 2:
                raise ValueError('Invalid choice')
        except ValueError:
            print('Invalid choice, please try again.')
            print()
            continue

        if choice == GENERATE_WALLET:
            generate_wallet()
            break
        elif choice == OWN_WALLET:
            use_own_wallet()


if __name__ == "__main__":
    main()
