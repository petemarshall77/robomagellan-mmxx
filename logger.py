from __future__ import print_function
import usb_probe
from time import asctime
from serial import Serial


class Logger:

    def __init__(self, doprint = True):
        # Open the log file
        self.doprint = doprint
        filename = "log/%s.%s" % (asctime(), 'log')
        self.file = open(filename, 'w')
        print("Log file opened:", filename)

    def write(self, message):
        datastring = "%s: %s\n" % (asctime(), message)
        if self.doprint == True:
            print(datastring.rstrip())
        self.file.write(datastring)
        self.file.flush()

    def __del__(self):
        self.file.close()
        print("Log file closed.")
