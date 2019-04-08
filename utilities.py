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

def open_serial_port():
    # find arduino tty
    arduino_path = '/dev/'
    arduino_tty = False
    for file in os.listdir(arduino_path):
        if file.startswith('tty.usb'):
            arduino_tty = arduino_path + file
            break

    # connect to arduino output
    ser = serial.Serial(arduino_tty, 9600) if arduino_tty else None
    return ser