import time
import random
import params
from proto import messages_pb2
import redis as _redis

redis = _redis.Redis(host='localhost', port=6379, db=0)

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007


def simulate_network_latency():
    # delay = random.randrange(params.NETWORK_LATENCY_MIN,
    #                          params.NETWORK_LATENCY_MAX) / 1000
    # time.sleep(delay)
    pass


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
