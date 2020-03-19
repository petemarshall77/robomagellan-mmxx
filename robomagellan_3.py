#
# robomagellan 3 - test the test mode
#
import robot
import time

robot = robot.Robot(mode = 'test')
if robot.ok_status == False:
    print("Robot ok_status is False")
    exit()
    
robot.wait_for_gps()
robot.powersteering.set_speed(3)
robot.powersteering.set_direction(280)
time.sleep(10)
robot.powersteering.stop_robot()
time.sleep(3)
robot.terminate()

