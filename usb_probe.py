#
# Probe serial devices on USB ports
#
from __future__ import print_function 
import subprocess, sys, re


def probe_port(port):
    """ Return udevadm data for port or None if not found """
    command = "udevadm info -a -n %s" % port
    try:
        out = subprocess.check_output(command.split(),
                                      stderr=subprocess.STDOUT)
        return out.decode("utf-8")

    except:
        return None
    
def parse_port_info(info):
    """ Return manufacturer and serial id from udevadm command """
    regex = re.compile("{serial}==\"([\w\.:]+)\"")
    match = regex.search(info)
    if match:
        serial = match.group(1)
    regex = re.compile("{manufacturer}==\"(.+)\"")
    match = regex.search(info)
    if match:
        manufacturer = match.group(1)
    return (serial, manufacturer)


def get_ports():
    """ Get the list of active serial ports """
    port_families = ['/dev/ttyACM', '/dev/ttyUSB']
    ports = []
    for family in port_families:
        for num in range(10):
            port = "%s%s" % (family, num)
            probe_output = probe_port(port)
            if probe_output:
                ports.append((port, probe_output))
    return ports


def find_device(device):
    """ Given the device name, return the serial port id """
    ports = get_ports()
    for port_info in ports:
        port = port_info[0]
        serial, _ = parse_port_info(port_info[1])
        if serial == device:
            return port

    
def main():
    ports = get_ports()
    for port_info in ports:
        port = port_info[0]
        serial, manufacturer = parse_port_info(port_info[1])
        print(port, serial, manufacturer)

if __name__ == "__main__":
    main()
