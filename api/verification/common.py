from time import time


class DebugTimer():
    def __init__(self):
        self.time = time()
    def rap(self, message, level='debug'):
        now_time = time()
        run_time = (now_time - self.time) * 1000
        print(f'{run_time:.1f}ms - {message}')
        self.time = now_time