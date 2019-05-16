from enum import Enum
import struct
import threading
import time

from python.threads import *  # CommandThread, ListenerThread
from python.utilities import *  # CustomQueue, open_serial_port
from python.database import *  # plants, garden


class Order(Enum):
    START_BYTE = 120
    HELLO = 10
    ALREADY_CONNECTED = 1
    ERROR = 2
    RECEIVED = 3
    CHECKSUM = 4

    REQUEST_SENSOR = 5
    SENSOR_MSG = 6
    ACTION_WATER_PLANT = 7
    # ACTION_STOP_WATER = 9
    # WATERING_FINISHED = 10


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


def generate_checksum(list):
    checksum = int(Order.START_BYTE.value)
    for i in list:
        checksum = checksum + i
    return checksum

def timeout_milliseconds(timeout):
    milli_sec = int(round(time.time() * 1000))
    nothing = 0
    while (int(round(time.time() * 1000)) - milli_sec < timeout):
        nothing = 1

def decode_order(messages):
    debug = False
    try:
        order = (messages[0])
        if order == Order.START_BYTE:
            msg = "START MSG"
        elif order == Order.HELLO:
            msg = "HELLO"
        elif order == Order.ALREADY_CONNECTED:
            msg = "ALREADY_CONNECTED"
        elif order == Order.ERROR:
            error_code = (messages[1])
            msg = "Error {}".format(error_code)
            print(msg)
        elif order == Order.RECEIVED:
            msg = "ARDUINO RECEIVED"
        elif order == Order.START_BYTE:
            msg = "START"
        elif order == Order.SENSOR_MSG:
            sensor = messages[1]
            sensor_data = messages[2]
            msg = "sensormsg {}".format(sensor_data)
            if sensor == 20:
                sensor_values["temperature value"] = sensor_data / 10;
            elif sensor == 21:
                sensor_values["airhumidity value"] = sensor_data / 10;
            elif sensor == 0:
                sensor_values["lightsensor value"] = sensor_data
                print("light: " + str(sensor_data))
            elif sensor == 1:
                garden[0]["humiditysensor value"] = sensor_data
                print("hum1: " + str(sensor_data))
            elif sensor == 2:
                garden[1]["humiditysensor value"] = sensor_data
            elif sensor == 3:
                garden[2]["humiditysensor value"] = sensor_data
            elif sensor == 4:
                garden[3]["humiditysensor value"] = sensor_data
            elif sensor == 5:
                garden[4]["humiditysensor value"] = sensor_data
            elif sensor == 6:
                garden[5]["humiditysensor value"] = sensor_data

            else:
                msg = ""
                print("Unknown Sensor", sensor)

        else:
            msg = ""
            print("Unknown Order", order)
        if debug:
            print(msg)
    except Exception as e:
        print("Error decoding order {}: {}".format(messages[0], e))
        print('byte={0:08b}'.format(messages[0]))


def addtoq(self, element):
    self.queue.insert(0, element)


class WaterProgram(object):
    def __init__(self):
        self.TEMPERATURE_SENSOR = 20
        self.AIRHUMIDITY_SENSOR = 21
        self.LIGHT_SENSOR = 0
        self.HUMIDITY_SENSOR_1 = 1
        self.HUMIDITY_SENSOR_2 = 2
        self.HUMIDITY_SENSOR_3 = 3
        self.HUMIDITY_SENSOR_4 = 4
        self.HUMIDITY_SENSOR_5 = 5
        self.HUMIDITY_SENSOR_6 = 6

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
                timeout_milliseconds(2000)
                #time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")

        self.command_queue = CustomQueue(20)
        self.n_messages_allowed = 10
        self.n_received_tokens = threading.Semaphore(self.n_messages_allowed)
        self.serial_lock = threading.Lock()
        self.exit_event = threading.Event()

        print("Starting Communication Threads")

        self.threads = [
            CommandThread(ser, self.command_queue, self.exit_event, self.n_received_tokens, self.serial_lock),
            ListenerThread(ser, self.exit_event, self.n_received_tokens, self.serial_lock)]
        for t in self.threads:
            t.start()

    def water_plant(self, angle, quantity):
        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.ACTION_WATER_PLANT, angle, quantity))
        checksum = generate_checksum([Order.ACTION_WATER_PLANT.value, angle, quantity])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

    def retrieve_all_sensor_data(self):
        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.TEMPERATURE_SENSOR, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.TEMPERATURE_SENSOR])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.AIRHUMIDITY_SENSOR, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.AIRHUMIDITY_SENSOR])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.LIGHT_SENSOR, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.LIGHT_SENSOR])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_1, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.HUMIDITY_SENSOR_1])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

        #self.command_queue.put((Order.START_BYTE, -1, -1))
        #self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_2, -1))
        #checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.HUMIDITY_SENSOR_2])
        #self.command_queue.put((Order.CHECKSUM, checksum))

        #self.command_queue.put((Order.START_BYTE, -1, -1))
        #self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_3, -1))
        #checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.HUMIDITY_SENSOR_3])
        #self.command_queue.put((Order.CHECKSUM, checksum, -1))

        # Humidity sensor 4,5,6 should be added in the real system.

    def daily_water(self):
        for i in range(0, 6):
            type = garden[i]["type"]
            if (type > 0) and (garden[i]["humiditysensor value"] <  plants[type]["humidity threshold max"]):
                if sensor_values["air humidity value"] < sensor_values["air humidity threshold"]:
                    self.water_plant(garden[i]["angle"], plants[garden[i]["type"]]["water quantity"])

    def evaluate_sensor_data(self):
        for i in range(0,5):
            quantity=0
            if garden[i]["type"]>0 and sensor_values["airhumidity value"] < sensor_values["air humidity threshold"]:
                if garden[i]["humiditysensor value"] < plants[garden[i]["type"]]["humidity threshold min"]:
                    quantity = plants[garden[i]["type"]]["water quantity"]
                if sensor_values["temperature value"] > sensor_values["temperature high threshold"]:
                    quantity += (plants[garden[i]["type"]]["water quantity"])/2;
                elif sensor_values["temperature value"] > sensor_values["temperature low threshold"] and sensor_values["lightsensor value"] > plants[garden[i]["type"]]["light intensity threshold"]:
                    quantity += (plants[garden[i]["type"]]["water quantity"])/2;
            if quantity > 0:
                self.water_plant(garden[i]["angle"], round(quantity))




    def run(self):
        bol = True
        i =1
        while bol:
            timeout_milliseconds(2000)
            self.evaluate_sensor_data()
            self.retrieve_all_sensor_data()
            bol = False






def main():
    wp = WaterProgram()
    wp.run()


if __name__ == "__main__":
    main()
