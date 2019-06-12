import time
from proto import messages_pb2

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007


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
