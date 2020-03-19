#
# speedometer.py - interface to speedomter
# to do- move except down and also power gain problems
import usb_probe
import robo_config
import serial
from  threaded import Threaded

class Speedometer(Threaded):

    def __init__(self, logger):
        super().__init__('Speedometer', logger)
        port = usb_probe.find_device(robo_config.speedometer_device)
        if port == None:
            print("Can't find serial port for device", robo_config.speedometer_device)
            return
        self.serial = serial.Serial(port, 9600)
        self.speed = 0
        self.distance = 0
        self.start()
        
    def run(self):
        _ = self.serial.readline()      # read and discard potentailly incomplete first read 
        while self._running == True:
            line = self.serial.readline()
            try:
                self.counts_per_second = float(line.decode('ascii').split(',')[0])
            except ValueError:
                print("bad data: ",line)
            self.speed = self.counts_per_second * robo_config.speedometer_calibration
            self.rotation_count = int(line.decode('ascii').split(',')[1])
            self.distance = self.rotation_count * robo_config.speedometer_calibration
            
    def get_values(self):

        return self.counts_per_second, self.rotation_count

    def get_speed_and_distance(self):
        
        return self.speed, self.distance
