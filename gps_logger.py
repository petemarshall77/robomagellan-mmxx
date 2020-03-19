#
# gps_logger.py - log gps data
#
from __future__ import print_function
from nav_math import get_distance_and_bearing
import robo_config
import usb_probe
import serial


def parse_gps_rmc(data):
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

    # Latitude
    lat = int(fields[3][0:2]) + (float(fields[3][2:])/60.0)
    if fields[4] == 'S':
        lat *= -1

    # Longitude
    lon = int(fields[5][0:3]) + (float(fields[5][3:])/60.0)
    if fields[6] == 'W':
        lon *= -1

    # Speed
    speed = float(fields[7])

    # Track
    track = float(fields[8])

    return time, seconds, status, lat, lon, speed, track


def main():
    gps_serial_port = usb_probe.find_device(robo_config.gps_device)
    if gps_serial_port == None:
        print("Can't find serial port for device", robo_config.gps_device)
        return

    with serial.Serial(gps_serial_port, 4800) as ser:
        # Print a header line (CSV format)
        print('time', 'seconds', 'status', 'lat', 'lon', 'delta_lat', 
              'delta_lon', 'distance', 'bearing', 'speed', 'track',
              sep=',')

        # Ignore (potentally incomplete) line recieved
        _ = ser.readline()

        # Process 1st RMC line
        line = ser.readline()
        while line.decode('utf-8').split(',')[0] != '$GPRMC':
            line = ser.readline()
        init_time, init_seconds, status, init_lat, init_lon, speed, track = \
            parse_gps_rmc(line)
        print(init_time, 0, status, init_lat, init_lon, 0, 0, 0, 0,
              speed, track, sep=',')

        # Process subsequent RMC lines
        while True:
            line = ser.readline()
            if line.decode('utf-8').split(',')[0] == '$GPRMC':
                time, seconds, status, lat, lon, speed, track = \
                    parse_gps_rmc(line)

                # Process seconds
                seconds = seconds - init_seconds
                if seconds < 0:
                    seconds += 24*3600

                # Heading and distance
                dist, head = get_distance_and_bearing(init_lat, init_lon,
                                                      lat, lon)
                
                # Delta latitude and longitude
                delta_lat, _  = get_distance_and_bearing(init_lat, lon,
                                                      lat, lon)
                if head >= 90 and head <= 270:
                    delta_lat *= -1
                delta_lon, _ = get_distance_and_bearing(lat, init_lon,
                                                      lat, lon)
                if head >= 180 and head <= 360:
                    delta_lon *= -1


                # Print the output
                print(time, seconds, status, lat, lon, delta_lat,
                      delta_lon, dist, head, speed, track, sep=',')
    


if __name__ == "__main__":
    main()
