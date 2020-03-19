#
# robomagellan 1 - test robot object
#
import robot
import time

robot = robot.Robot()
robot.wait_for_gps()
time.sleep(5)
robot.terminate()

