from enum import Enum
import struct
import threading
import time
from .threads import CommandThread, ListenerThread

from .utilities import CustomQueue, open_serial_port

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

        try:
            ser = open_serial_port()
        except Exception as e:
            raise e
        is_connected = False
        # Initialize communication with Arduino
        while not is_connected:
            print("Waiting for arduino...")
            write_order(ser, Order.HELLO)
            bytes_array = bytearray(ser.read(1))
            if not bytes_array:
                time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")

        # Create Command queue for sending orders
        self.command_queue = CustomQueue(2)

        # Number of messages we can send to the Arduino without receiving an acknowledgment
        self.n_messages_allowed = 3
        self.n_received_tokens = threading.Semaphore(self.n_messages_allowed)

        # Lock for accessing serial file (to avoid reading and writing at the same time)
        self.serial_lock = threading.Lock()

        # Event to notify threads that they should terminate
        self.exit_event = threading.Event()

        print("Starting Communication Threads")

        # Initialize Threads for arduino communication
        self.threads = [CommandThread(ser, self.command_queue, self.exit_event, self.n_received_tokens, self.serial_lock),
                   ListenerThread(ser, self.exit_event, self.n_received_tokens, self.serial_lock)]
        # Start threads
        for t in self.threads:
            t.start()


    clear = True
    def run(self):


        # Send 3orders to the arduino
        # self.command_queue.put((Order.MOTOR, -56)) # Eks 1

        # End the threads
        self.exit_event.set()
        self.n_received_tokens.release()

        print("Exiting...")

        for t in self.threads:
            t.join()





if __name__ =="__main__":
    main = PythonCode()
    main.run()
