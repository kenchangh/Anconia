from proto import messages_pb2
from message_client import MessageClient
from crypto import Keypair, SigningKey, NIST192p


def generate_wallet():
    keypair = Keypair()
    print()
    print('Your new wallet address is:', keypair.nice_address)
    print('Please keep your private key safe!')
    print(keypair.privkey.to_string().hex())


def print_account(message_client):
    balance_response = message_client.check_balance()

    print()
    print('Address:', balance_response.address)
    print('Balance:', f'{balance_response.balance:,} ANC')
    print('Nonce:', balance_response.nonce)
    print()


def send_transaction(message_client):
    recipient_addr = None
    amount = None

    while True:
        print('Enter the recipient address:', end=" ")
        recipient_addr = input()

        if len(recipient_addr) != 23 and recipient_addr[:3] != 'anc':
            print('Invalid address!\n')
            continue

        print('Enter the amount to send:', end=" ")

        amount = input()
        try:
            amount = int(amount)
            break
        except ValueError:
            print('Invalid amount!\n')
            continue

    msg_obj = message_client.generate_txn_object(recipient_addr, amount)
    msg = MessageClient.create_message(
        messages_pb2.TRANSACTION_MESSAGE, msg_obj)
    message_client.send_message(message_client.FIXED_PEERS[0], msg)
    print()
    print('Broadcasted transaction to network!')
    print(f'Transaction hash: {msg_obj.hash}')


def use_own_wallet():
    print()
    print('Insert your private keys:', end=' ')
    privkey_input = bytes.fromhex(input())
    privkey = SigningKey.from_string(privkey_input, curve=NIST192p)
    keypair = Keypair.from_private_key(privkey)

    message_client = MessageClient(light_client=True, own_key=keypair)
    print_account(message_client)

    while True:
        print('What would you like to do?')
        print('1. Send ANC')
        print('2. Receive ANC')
        print('Input your choice:', end=" ")
        choice = input()

        SEND = 1
        RECEIVE = 2

        try:
            choice = int(choice)
            if choice != SEND and choice != RECEIVE:
                raise ValueError('Invalid choice')
        except ValueError:
            print('Invalid choice, please try again.')
            print()
            continue

        if choice == SEND:
            send_transaction(message_client)
            break
        elif choice == RECEIVE:
            # use_own_wallet()
            break


def send_receive_anc():
    print('You can either:')
    print('1. Send ANC to another user')
    print('2. Receive ANC to another user')


def check_tx():
    txhash = None

    while True:
        print()
        print('Enter your transaction hash:', end=" ")
        txhash = input()

        if len(txhash) != 64:
            print('Invalid transaction hash!')
            print()
            continue
        else:
            break

    message_client = MessageClient(light_client=True)
    txn = message_client.check_tx_status(txhash)

    print()

    if not txn.accepted:
        print('Your transaction is not accepted yet.')
    else:
        print('Your transaction is accepted.')
    if not txn.chit and txn.queried:
        print('Your transaction has no early commitments yet.')
    elif txn.queried and txn.chit:
        print('Your transaction has early commitments.')

    print()
    print('RAW TRANSACTION:')
    print(txn)


def main():
    print('Welcome to Anconia blockchain.')

    while True:
        print('Please select one of the options below:')
        print('1. Generate wallet')
        print('2. Use own wallet')
        print('3. Check transaction status')
        print('Input your choice:', end=" ")
        choice = input()

        GENERATE_WALLET = 1
        OWN_WALLET = 2
        CHECK_TX = 3

        try:
            choice = int(choice)
            if choice != GENERATE_WALLET and choice != OWN_WALLET \
                    and choice != CHECK_TX:
                raise ValueError('Invalid choice')
        except ValueError:
            print('Invalid choice, please try again.')
            print()
            continue

        if choice == GENERATE_WALLET:
            generate_wallet()
        elif choice == OWN_WALLET:
            use_own_wallet()
        elif choice == CHECK_TX:
            check_tx()
        break


if __name__ == "__main__":
    main()
