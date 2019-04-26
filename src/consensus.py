import random

NO_COLOR = 0
RED_COLOR = 1
BLUE_COLOR = 2


def slush_algorithm(message_server, transaction):
    QUERY_TIMEOUT = 10
    NETWORK_SAMPLE_SIZE = 10

    color = NO_COLOR

    """
    1. Start uncolored node
    2. On receive transaction, update own color to color of transaction sender
    3. Queries k sample
    4. Queried nodes return own color, or respond with that color if uncolored
    """

    query_nodes = []
    if len(message_server.peers) < NETWORK_SAMPLE_SIZE:
        query_nodes = list(message_server.peers)
    else:
        query_nodes = random.sample(
            message_server.peers, NETWORK_SAMPLE_SIZE)
