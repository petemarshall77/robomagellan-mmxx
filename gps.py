#
# gps.py - interface to gps device
#
import usb_probe
import robo_config
import serial
from threaded import *
from nav_math import get_distance_and_bearing


class GPS(Threaded):

    def __init__(self, logger, mode = 'real'):
        super().__init__('GPS', logger)
        port = usb_probe.find_device(robo_config.gps_device)
        if port == None:
            print("Can't find serial port for device", robo_config.gps_device)
            return
        self.serial = serial.Serial(port, 4800)
        self.init_values_set = False
        self.start()

    def run(self):
        _ = self.serial.readline()
        while self._running == True:
            line = self.serial.readline()
            if line.decode('ascii').split(',')[0] == '$GPRMC':
                self.time, self.seconds, self.status, \
                    self.lat, self.lon, \
                    self.speed, self.track = \
                    self.parse_gps_rmc(line)

                if self.status != 'A':
                    continue

                # Handle initial values
                if self.init_values_set == False \
                        and self.status == 'A':
                    self.init_values_set = True
                    self.init_seconds = self.seconds
                    self.init_lat = self.lat
                    self.init_lon = self.lon

                # Process seconds
                self.seconds = self.seconds - self.init_seconds
                if self.seconds < 0:
                    self.seconds += 24*3600

                # Heading and distance
                self.dist, self.head = \
                    get_distance_and_bearing(self.init_lat, self.init_lon,
                                             self.lat, self.lon)

                # Delta latitude and longitude
                self.delta_lat, _  = \
                    get_distance_and_bearing(self.init_lat, self.lon,
                                             self.lat, self.lon)
                if self.head >= 90 and self.head <= 270:
                    self.delta_lat *= -1

                self.delta_lon, _ = \
                    get_distance_and_bearing(self.lat, self.init_lon,
                                             self.lat, self.lon)
                if self.head >= 180 and self.head <= 360:
                    self.delta_lon *= -1

        self.logger.write('GPS terminated')

    def parse_gps_rmc(self, data):
        """ Parse GPS RMC sentence """
        fields = data.decode('utf-8').split(',')

        # Format time
        time = fields[1][:2] + ':' + \
            fields[1][2:4] + ':' + \
            fields[1][4:6]

        # Seconds since midnight
        seconds = int(fields[1][:2]) * 3600 + \
            int(fields[1][2:4]) * 60 + \
            int(fields[1][4:6])

        # GPS status
        status = fields[2]
        if status != 'A':
            return time, seconds, status, 0.0, 0.0, 0.0, 0.0
        
        # Latitude
        lat = int(fields[3][0:2]) + (float(fields[3][2:])/60.0)
        if fields[4] == 'S':
            lat *= -1

        # Longitude
        lon = int(fields[5][0:3]) + (float(fields[5][3:])/60.0)
        if fields[6] == 'W':
            lon *= -1

        # Speed (converted from knots to m/s)
        speed = float(fields[7]) * 0.514444

        # Track
        track = float(fields[8])

        return time, seconds, status, lat, lon, speed, track

    def get_values(self):

        try:
            if self.status != 'A':
                return None

            return self.time, self.seconds, self.status, \
            self.lat, self.lon, self.delta_lat, self.delta_lon, \
            self.dist, self.head, self.speed, self.track
        except AttributeError:
            return None
