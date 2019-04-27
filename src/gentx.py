import sys
from message_client import MessageClient
from consensus import slush_algorithm
from common import INVERSE_COLOR_MAP


def create_transaction(addr, port, color_str, amount=100):
    color_int = INVERSE_COLOR_MAP.get(color_str)
    if not color_int:
        return ValueError(f'No such color "{color_str}"')

    client = MessageClient(consensus_algorithm=slush_algorithm)
    msg = client.generate_transaction(color_int, amount)
    client.send_message((addr, port), msg)


if __name__ == '__main__':
    addr = sys.argv[1]
    port = int(sys.argv[2])
    color = sys.argv[3]
    create_transaction(addr, port, color)
