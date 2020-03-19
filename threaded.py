#
# threaded.py - provide basic threading capabilities
#
from serial import Serial
from threading import Thread

class Threaded:
    
    def __init__(self, name, logger):
        self.name = name
        self._running = False
        self.thread = Thread(target = self.run)
        self.logger = logger
        self.logger.write("Threaded %s starting" % self.name)

    def start(self):
        self.logger.write("Threaded starting thread %s" % self.name)
        self._running = True
        self.thread.start()

    def terminate(self):
        self.logger.write("terminating %s thread" % self.name)
        self._running = False

