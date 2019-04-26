from proto import messages_pb2
from common import create_message
import random


def slush_algorithm(message_server, transaction):
    QUERY_TIMEOUT = 10
    NETWORK_SAMPLE_SIZE = 10

    current_color = message_server.color

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

    for node in query_nodes:
        node_query = messages_pb2.NodeQuery()
        node_query.color = transaction.color
        msg = create_message(messages_pb2.NODE_QUERY_MESSAGE, node_query)
        response = message_server.send_message(node, msg)
        print(response)
