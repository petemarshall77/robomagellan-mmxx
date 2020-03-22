#
# Vrobot - virtual robot
#
from threaded import *
import time

class Vrobot(Threaded):

    def __init__(self, logger):

        super().__init__('vrobot', logger)
        # init variables etc
        self.logger = logger
        self.start()

    def run(self):

        while self._running == True:
            self.logger.write("Vrobot status")
            time.sleep(1)
        
