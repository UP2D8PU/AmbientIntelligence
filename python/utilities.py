from __future__ import print_function, division, absolute_import

import sys
import glob

try:
    import queue
except ImportError:
    import Queue as queue

import serial
import os




class CustomQueue(queue.Queue):
    """
    A custom queue subclass that provides a :meth:`clear` method.
    """

    def clear(self):
        """
        Clears all items from the queue.
        """

        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
            self.queue.clear()
            self.not_full.notify_all()


# From https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
# Returns a list of available serial ports (based on if you have windows or mac computer
# glob.glob(pathname) -> Return a possibly-empty list of path names that match pathname,
def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.usbmodem1421')
        # or usbmodem1411
    else:
        raise EnvironmentError('Unsupported platform')

    results = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            results.append(port)
        except (OSError, serial.SerialException):
            pass
    return results

# Open serial port (for communication with Arduino)
def open_serial_port(serial_port=None, baudrate=115200, timeout=0, write_timeout=0):
    #If serial port is not specified, it can be detected with get_serial_ports()
    if serial_port is None:
        serial_port = get_serial_ports()[0]
        print(serial_port)
    return serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout, writeTimeout=write_timeout)
