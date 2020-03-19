#
# speedometer_test.py - quick test of the Speedometer class
#
import logger
import speedometer
import time

my_logger = logger.Logger()
my_speedometer = speedometer.Speedometer(my_logger)

my_speedometer.start()
time.sleep(3)

while True:
    print(my_speedometer.get_values())
    time.sleep(1)
