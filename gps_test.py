#
# gps_test.py - quick test of the GPS class
#
import logger
import gps
import time

my_log = logger.Logger()
my_gps = gps.GPS(my_log)

my_gps.start()
time.sleep(3)

while True:
    print(my_gps.get_values())
    time.sleep(1)

