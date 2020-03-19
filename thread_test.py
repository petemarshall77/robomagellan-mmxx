#
# thread-test.py - quick test of the threaded class
#
from threaded import *
import time

class ThreadTest(Threaded):

    def __init__(self, logger):
        super().__init__('ThreadTest', None, None, logger)

    def run(self):
        while self._running == True:
            self.logger.write("ThreadTest is running")
            time.sleep(3)

        self.logger.write('ThreadTest terminated')
