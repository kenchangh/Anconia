import random
import math
import logging
from proto import messages_pb2
from message_client import MessageClient
from common import COLOR_MAP, INVERSE_COLOR_MAP

QUERY_ROUNDS = 10
QUERY_TIMEOUT = 10
NETWORK_SAMPLE_SIZE = 10
ALPHA_PARAM = 0.5
BETA_PARAM = 10

logger = logging.getLogger('main')


def the_other_color(color):
    if color == messages_pb2.RED_COLOR:
        return messages_pb2.BLUE_COLOR
    return messages_pb2.RED_COLOR


def snowflake_algorithm(message_client, txn_color):
    current_color = txn_color
    query_count = 0
    other_color = the_other_color(current_color)
    logger.debug(f'Transaction color is {COLOR_MAP[current_color]}')

    """
    1. Start uncolored node
    2. On receive transaction, update own color to color of transaction sender
    3. Queries k sample
    4. Queried nodes return own color, or respond with that color if uncolored
    """

    flip_threshold = math.floor(ALPHA_PARAM * NETWORK_SAMPLE_SIZE)
    color_responses = {
        messages_pb2.RED_COLOR: 0,
        messages_pb2.BLUE_COLOR: 0,
    }

    while query_count < BETA_PARAM:
        query_nodes = []
        if len(message_client.peers) < NETWORK_SAMPLE_SIZE:
            query_nodes = list(message_client.peers)
        else:
            query_nodes = random.sample(
                message_client.peers, NETWORK_SAMPLE_SIZE)

        for node in query_nodes:
            node_query = messages_pb2.NodeQuery()
            node_query.color = current_color
            msg = MessageClient.create_message(
                messages_pb2.NODE_QUERY_MESSAGE, node_query)
            response = message_client.send_message(node, msg)
            if not response:
                continue
            query_msg = MessageClient.get_sub_message(
                messages_pb2.NODE_QUERY_MESSAGE, response)

            logger.debug(
                f"Query result is '{COLOR_MAP[query_msg.color]}'")
            if query_msg.color == messages_pb2.RED_COLOR or query_msg.color == messages_pb2.BLUE_COLOR:
                color_responses[query_msg.color] += 1
            else:
                raise ValueError(f'Invalid color {query_msg.color}')

        if color_responses[other_color] > flip_threshold:
            query_count = 0
            logger.info(
                f'Flipped to color {COLOR_MAP[other_color]}')
            current_color = other_color
        elif color_responses[current_color] > flip_threshold:
            query_count += 1
            logger.info(
                f'Remained current color {COLOR_MAP[current_color]}')

    logger.info(f'Concluded with color {COLOR_MAP[current_color]}')
    message_client.color = current_color
    return current_color
