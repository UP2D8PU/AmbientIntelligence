from __future__ import print_function, division, absolute_import

import threading
import time

import serial
import python.waterprogram as wp
from .waterprogram import *
from .utilities import *

rate = 1 / 2000  # in millisec: 2000 Hz (limit the rate of communication with the arduino)


"""
Queues: communicate between threads
A thread that has the data puts them on the queue (a.k.a producer)
The other thread picks items from the queue (a.k.a consumer).

"""

class CommandThread(threading.Thread):
    """
    Thread that send orders to the arduino
    it blocks if there no more send_token left.

    :param serial_file: (Serial object)
    :param command_queue: (Queue)
    :param exit_event: (Threading.Event object)
    :param n_received_tokens: (threading.Semaphore)
    :param serial_lock: (threading.Lock)
    """

    def __init__(self, serial_file, command_queue, exit_event, n_received_tokens, serial_lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.serial_file = serial_file
        self.command_queue = command_queue
        self.exit_event = exit_event
        self.n_received_tokens = n_received_tokens
        self.serial_lock = serial_lock
        self.messages = []
    """
    Method representing the thread’s activity.
    You may override this method in a subclass. 
    The standard run() method invokes the callable object passed to the object’s 
    constructor as the target argument, if any, with sequential and keyword arguments 
    taken from the args and kwargs arguments, respectively.
    """
    def run(self):
        while not self.exit_event.is_set():
            self.n_received_tokens.acquire()
            if self.exit_event.is_set():
                break
            try:
                order, param1,param2 = self.command_queue.get_nowait()
            except queue.Empty:
                time.sleep(rate)
                self.n_received_tokens.release()
                continue

            with self.serial_lock:
                print(order, param1, param2)
                if order.value != wp.Order.CHECKSUM.value:
                    wp.write_order(self.serial_file, order)
                    print("order written", order)
                    if param1 != -1:
                        print("param1:", param1)
                        wp.write_i8(self.serial_file, param1)
                    if param2 != -1:
                        print("param2:", param2)
                        wp.write_i16(self.serial_file, param2)
                else:
                    wp.write_i16(self.serial_file, param1)

                self.messages=[]
            time.sleep(rate)
        print("Command Thread Exited")


class ListenerThread(threading.Thread):
    """
    Thread that listen to the Arduino
    It is used to add send_tokens to the n_received_token

    :param serial_file: (Serial object)
    :param exit_event: (threading.Event object)
    :param n_received_tokens: (threading.Semaphore)
    :param serial_lock: (threading.Lock)
    """

    def __init__(self, serial_file, exit_event, n_received_tokens, serial_lock):
        threading.Thread.__init__(self)
        self.deamon = True
        self.serial_file = serial_file
        self.exit_event = exit_event
        self.n_received_tokens = n_received_tokens
        self.serial_lock = serial_lock
        self.start_received = False
        self.messages = []
        self.checksum = 0

    def run(self):
        while not self.exit_event.is_set():
            try:
                start_byte = bytearray(self.serial_file.read(1))
            except serial.SerialException:
                time.sleep(rate)
                continue
            if not start_byte:
                time.sleep(rate)
                continue
            start = start_byte[0]

            with self.serial_lock:
                try:
                    order = wp.Order(start)
                except ValueError:
                    continue
                if order == wp.Order.START_BYTE:
                    self.start_received = True
                    self.checksum = wp.Order.START_BYTE.value

                if order == wp.Order.ERROR:

                    error = wp.read_i16(self.serial_file)

                    self.messages.append(order)
                    self.messages.append(error)
                    wp.decode_order(self.messages)

                if self.start_received:

                    order = wp.read_i8(self.serial_file)
                    try:
                        order = wp.Order(order)
                    except ValueError:
                        continue
                    if order == wp.Order.RECEIVED:
                        print("Received message")
                        self.checksum = self.checksum + order.value

                        received_checksum = wp.read_i16(self.serial_file)

                        if self.checksum - received_checksum == 0:
                            self.messages.append(order)
                            self.n_received_tokens.release()
                            self.n_received_tokens.release()
                            self.n_received_tokens.release()

                        else:
                            print("CHECKSUM ERROR")
                    if order == wp.Order.SENSOR_MSG:
                        sensor = -1

                        sensor = wp.read_i8(self.serial_file)
                        value = wp.read_i16(self.serial_file)
                        self.checksum = self.checksum + order.value + sensor + value

                        received_checksum = wp.read_i16(self.serial_file)

                        if self.checksum-received_checksum == 0:
                            self.messages.append(order)
                            self.messages.append(sensor)
                            self.messages.append(value)
                            wp.decode_order(self.messages)

                        else:
                            print("CHECKSUM ERROR")

                    self.checksum = 0
                    self.messages = []
                    self.start_received = False
            time.sleep(rate)
        print("Listener Thread Exited")
