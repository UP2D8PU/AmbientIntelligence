from __future__ import print_function, division, absolute_import

import threading
import time

import serial

from python.waterprogram import *# write_order, Order, write_i8, decode_order
from python.utilities import *# queue

rate = 1 / 2000  # 2000 Hz (limit the rate of communication with the arduino)


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
                if order.value != Order.CHECKSUM.value:
                    write_order(self.serial_file, order)
                    print("order written " + str(order.value))
                    if param1 != -1:
                        write_i8(self.serial_file, param1)
                    if param2 != -1:
                        write_i8(self.serial_file, param2)
                else:
                    write_i16(self.serial_file, param1)

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
                    order = Order(start)
                except ValueError:
                    continue
                if order == Order.START_BYTE:
                    self.start_received = True
                    self.checksum = Order.START_BYTE.value

                if order == Order.ERROR:
                    error = read_i16(self.serial_file)
                    self.messages.append(self, order.value)
                    self.messages.append(self, error)
                    decode_order(self.messages)

                if self.start_received:
                    try:
                        order = read_i8(self.serial_file)
                    except serial.SerialException:
                        time.sleep(rate)
                        continue
                    if not order:
                        time.sleep(rate)
                        continue
                    try:
                        order = Order(order)
                    except ValueError:
                        continue
                    if order == Order.RECEIVED:
                        print("Recieved message")
                        self.checksum = self.checksum + order.value
                        received_checksum = read_i16(self.serial_file)
                        if self.checksum - received_checksum == 0:
                            self.messages.append(self, order.value)
                            self.n_received_tokens.release()
                        else:
                            print("CHECKSUM ERROR")

                    if order == Order.SENSOR_MSG:
                        sensor = read_i8(self.serial_file)
                        value = read_i16(self.serial_file)

                        self.checksum = self.checksum + order.value +sensor + value
                        received_checksum = read_i16(self.serial_file)

                        if self.checksum-received_checksum == 0:
                            self.messages.append(self, order)
                            self.messages.append(self, sensor)
                            self.messages.append(self, value)
                            decode_order(self.messages)

                        else:
                            print("CHECKSUM ERROR")

                    self.checksum = 0
                    self.messages = []
            time.sleep(rate)
        print("Listener Thread Exited")
