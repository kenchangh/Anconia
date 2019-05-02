import time
from proto import messages_pb2

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

COLOR_MAP = {
    messages_pb2.RED_COLOR: 'red',
    messages_pb2.BLUE_COLOR: 'blue',
}

INVERSE_COLOR_MAP = {
    'red': messages_pb2.RED_COLOR,
    'blue': messages_pb2.BLUE_COLOR,
}


def exponential_backoff(logger, function, args, timeout=1, max_retry=5, expected_exception=Exception):
    exp_timeout = timeout
    retry_count = 1

    while True:
        try:
            return function(*args)
        except expected_exception as e:
            logger.error(e)
            if retry_count >= max_retry:
                err = TimeoutError(
                    f"Max retries of {max_retry} times exceeded on function '{function.__name__}'")
                logger.error(err)
                return err
            time.sleep(exp_timeout)
            retry_count += 1
            exp_timeout = exp_timeout ** retry_count
