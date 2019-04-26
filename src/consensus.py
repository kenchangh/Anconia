from proto import messages_pb2
from message_client import MessageClient
import random


def slush_algorithm(message_client, transaction):
    QUERY_TIMEOUT = 10
    NETWORK_SAMPLE_SIZE = 10

    current_color = message_client.color

    """
    1. Start uncolored node
    2. On receive transaction, update own color to color of transaction sender
    3. Queries k sample
    4. Queried nodes return own color, or respond with that color if uncolored
    """

    query_nodes = []
    if len(message_client.peers) < NETWORK_SAMPLE_SIZE:
        query_nodes = list(message_client.peers)
    else:
        query_nodes = random.sample(
            message_client.peers, NETWORK_SAMPLE_SIZE)

    for node in query_nodes:
        node_query = messages_pb2.NodeQuery()
        node_query.color = transaction.color
        msg = MessageClient.create_message(
            messages_pb2.NODE_QUERY_MESSAGE, node_query)
        response = message_client.send_message(node, msg)
        print(response)
