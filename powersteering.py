#
# powersteering.py - implements power and steering control, interfaces to CHIAS
#
import usb_probe
import robo_config
import speedometer
import serial
from threaded import Threaded
import time

class Powersteering(Threaded):

    def __init__(self, logger, gps, mode = 'real'):
        if mode == 'test':
            print("Powerster]ering is in test mode")
        super().__init__('PowerSteering', logger)
        self.logger = logger
        self.gps = gps
        port = usb_probe.find_device(robo_config.chias_device)
        if port == None:
            print("Can't find serial port for device", robo_config.chias_device)
            return
        self.serial = serial.Serial(port, 9600)
        self.speedometer = speedometer.Speedometer(self.logger)
        self.speed = 0
        self.direction = 0
        self.power = 1500
        self.steering = 1500
        self.start()

    def run(self):
        
        while self._running == True:
            # get the current speed and direction
            robot_speed, _ = self.speedometer.get_speed_and_distance()
            gps_data = self.gps.get_values()
            if gps_data == None:
                self.logger.write("No gps data")
                time.sleep(1)
                continue
        
            track = self.gps.get_values()[10]
            self.logger.write("robot speed: %d, robot track: %d" % (robot_speed, track))
            # adjust the power to make the speed correct
            if self.speed == 0:
                self.power = 1500
            else:
                delta_speed = (self.speed - robot_speed)
                delta_power = int(delta_speed * robo_config.speed_servo_gain)
                self.power += delta_power
                if self.power > robo_config.power_limit:
                    self.power = robo_config.power_limit
                if self.power < 1500:
                    self.power = 1500

            # adjust the steering to move to the desired direction
            delta_angle = (self.direction - track)
            if delta_angle > 180:
                delta_angle = delta_angle - 360
            elif delta_angle < -180:
                delta_angle = 360 + delta_angle
                
            self.steering = int(1500 + delta_angle * robo_config.steering_servo_gain)
            if self.steering > robo_config.max_right_steer:
                self.steering = robo_config.max_right_steer
            elif self.steering < robo_config.max_left_steer:
                self.steering = robo_config.max_left_steer
            
            # send to chias
            self.chias_command = ((str(int(self.steering)) + "," + str(int(self.power)) + "\n").encode('ascii'))
            self.serial.write(self.chias_command)
            self.serial.flush()

            time.sleep(0.2)

        self.speedometer.terminate()
        
    def set_speed(self, speed):
        self.speed = speed
        self.logger.write("PowerSteering: speed set to %d" % self.speed)

    def set_direction(self, direction):
        self.direction = direction
        self.logger.write("PowerSteering: direction set to %d" % self.direction)
            
    def stop_robot(self):
        self.set_speed(0)

