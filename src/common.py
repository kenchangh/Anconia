from proto import messages_pb2

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

# TO BE UPDATED PERIODICALLY
ATTR_NAMES = {
    messages_pb2.NODE_QUERY_MESSAGE: 'node_query',
    messages_pb2.JOIN_MESSAGE: 'join',
    messages_pb2.TRANSACTION_MESSAGE: 'transaction',
}


def create_message(message_type, sub_msg):
    common_msg = messages_pb2.CommonMessage()
    common_msg.message_type = message_type

    attr_name = ATTR_NAMES.get(message_type)
    if not attr_name:
        raise ValueError(
            f'Invalid message_type {message_type}, or ATTR_NAMES not updated')

    getattr(common_msg, attr_name).CopyFrom(sub_msg)
    msg = common_msg.SerializeToString()
    return msg
