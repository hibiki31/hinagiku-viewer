import time

from mixins.log import setup_logger

logger = setup_logger(__name__)


class DebugTimer:
    def __init__(self):
        self.time = time()
    def rap(self, message, level='debug'):
        now_time = time()
        run_time = (now_time - self.time) * 1000
        if level == 'info':
            logger.debug(f'{run_time:.1f}ms - {message}')
        else:
            logger.debug(f'{run_time:.1f}ms - {message}')
        self.time = now_time
