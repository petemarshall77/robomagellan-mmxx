#
# Vrobot - virtual robot
#
from threaded import *
import time
import math

class Vrobot(Threaded):

    def __init__(self, logger):

        super().__init__('vrobot', logger)
        self.logger = logger

        self.latitude = 33.1
        self.logitude = -118.4
        self.xpos = 0
        self.ypos = 0
        self.heading = 135
        self.speed = 0.1

        self.power = 1500
        self.steer = 1500

        self.steering_angle = 0
        
        self.start()

    def run(self):

        while self._running == True:
            distance_travelled = self.speed
            self.xpos += distance_travelled * math.cos((90-self.heading)*(math.pi/180))
            self.ypos += distance_travelled * math.sin((90-self.heading)*(math.pi/180))
            self.logger.write("Vrobot xpos=%f ypos=%f speed=%f" % (self.xpos, self.ypos, self.speed))
            time.sleep(1)


    def set_power_and_steering(self, power_val, steer_val):
        self.speed = 1.78/(1580-1500)*(power_val-1500)
        
