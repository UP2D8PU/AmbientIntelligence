#from arduino import ser
from enum import Enum
import struct
import threading
import time

class Order(Enum):
    HELLO = 0
    ALREADY_CONNECTED = 1
    ERROR = 2
    RECEIVED = 3
    STOP = 4

    REQUEST_SENSOR = 5
    SENSOR_MSG = 6
    ACTION_WATER_PLANT = 7
    ACTION_WATER_QUANTITY = 8
    ACTION_STOP_WATER = 9
    WATERING_FINISHED = 10

def read_order(f):
    return Order(read_i8(f))

def read_i8(f):
    return struct.unpack('<b', bytearray(f.read(1)))[0]


def read_i16(f):
    return struct.unpack('<h', bytearray(f.read(2)))[0]


def write_i8(f, value):
    if -128 <= value <= 127:
        f.write(struct.pack('<b', value))
    else:
        print("Value error:{}".format(value))


def write_order(f, order):
    write_i8(f, order.value)


def write_i16(f, value):
    f.write(struct.pack('<h', value))


def decode_order(f, byte, debug=False):
    try:
        order = Order(byte)
        if order == Order.HELLO:
            msg = "HELLO"
        elif order == Order.ALREADY_CONNECTED:
            msg = "ALREADY_CONNECTED"
        elif order == Order.ERROR:
            error_code = read_i16(f)
            msg = "Error {}".format(error_code)
        elif order == Order.RECEIVED:
            msg = "ARDUINO RECEIVED"
        elif order == Order.STOP:
            msg = "STOP"
        elif order == Order.SENSOR_MSG:
            sensor_data = read_i8(f)
            msg = "sensormsg {}".format(sensor_data)
        elif order == Order.WATERING_FINISHED:
            clear = True
        else:
            msg = ""
            print("Unknown Order", byte)
        if debug:
            print(msg)
    except Exception as e:
        print("Error decoding order {}: {}".format(byte, e))
        print('byte={0:08b}'.format(byte))

def addtoq(self,element):
    self.queue.insert(0,element)


class PythonCode(object):
    def __init__(self):

        self.clear = True #If arduino has retrieved last message
        self.ready_to_water = True #If arduino are not busy watering other plants

        self.interval = interval
        thread = threading.Thread(target=self.run,args())
        thread.daemon = True
        thread.start()



    clear = True
    def run():
        while True:
            if (ser.available()>0):
                Order order = read_order()



            queue = list()
            if len(queue)>0 & clear == True > 0:
                write_order(queue.pop())


            #If action request from homepage
            if (clear == True):
                write_order()
                clear = False;
            else:
                queue.insert(order)





if __name__ =="__main__":
    main = PythonCode()
