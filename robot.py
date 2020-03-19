#
# robot.py -implements the robot
#
import logger
import gps
import powersteering
import time

class Robot():

    def __init__(self, mode = 'real'):
        if mode == 'test':
            print("Robot is in test mode")
        self.ok_status = False
        self.logger = logger.Logger()
        self.gps = gps.GPS(self.logger, mode = mode)
        self.powersteering = powersteering.Powersteering(self.logger, self.gps, mode = mode)
        if self.gps._running == False or  self.powersteering._running == False:
            self.logger.write("One or more robot components failed to start")
            return
        self.ok_status = True

    def terminate(self):
        self.logger.write("Robot terminating")
        self.gps.terminate()
        self.powersteering.terminate()
        time.sleep(3)  # allow terminating threads time to write to looger


    def wait_for_gps(self):
        while self.gps.get_values() == None:
            self.logger.write("Waiting for gps")
            time.sleep(1)


