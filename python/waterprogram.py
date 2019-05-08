from enum import Enum
import struct
import threading
import time
import schedule

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
    ACTION_WATER_QUANTITY = 8
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


def decode_order(messages):
    debug = False
    try:
        order = (messages[0])
        print(type(order))
        print(type(Order.ERROR.value))
        print(type(order - Order.ERROR.value))
        if order == Order.START_BYTE.value:
            msg = "START MSG"
        elif order == Order.HELLO.value:
            msg = "HELLO"
        elif order == Order.ALREADY_CONNECTED.value:
            msg = "ALREADY_CONNECTED"
        elif order == Order.ERROR.value:
            error_code = (messages[1])
            msg = "Error {}".format(error_code)
            print(msg)
        elif order == Order.RECEIVED.value:
            msg = "ARDUINO RECEIVED"
        elif order == Order.START_BYTE.value:
            msg = "START"
        elif order == Order.SENSOR_MSG.value:
            sensor = messages[1]
            sensor_data = messages[2]
            msg = "sensormsg {}".format(sensor_data)
            if sensor == 20:
                sensor_values["temperatur_value"] = sensor_data / 10;
            elif sensor == 21:
                sensor_values["airhumidity_value"] = sensor_data / 10;
            elif sensor == 2:
                sensor_values["lightsensor value"] = sensor_data
            elif sensor == 3:
                garden["0"]["humiditysensor value"] = sensor_data
            elif sensor == 4:
                garden["1"]["humiditysensor value"] = sensor_data
            elif sensor == 5:
                garden["2"]["humiditysensor value"] = sensor_data
            elif sensor == 6:
                garden["3"]["humiditysensor value"] = sensor_data
            elif sensor == 7:
                garden["4"]["humiditysensor value"] = sensor_data
            elif sensor == 8:
                garden["5"]["humiditysensor value"] = sensor_data

                sensor_values["updated"] == 1

            else:
                msg = ""
                print("Unknown Sensor", sensor)

        else:
            msg = ""
            print("Unknown Order", messages[0])
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
        self.LIGHT_SENSOR = 2
        self.HUMIDITY_SENSOR_1 = 3
        self.HUMIDITY_SENSOR_2 = 4
        self.HUMIDITY_SENSOR_3 = 5
        self.HUMIDITY_SENSOR_4 = 6
        self.HUMIDITY_SENSOR_5 = 7
        self.HUMIDITY_SENSOR_6 = 8
        self.test = True

        self.air_humidity_threshold  = 85
        self.temperature_threshold = 20
        self.light_intensity_threshold = 100 

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
            print(byte)
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")

        self.command_queue = CustomQueue(20)
        self.n_messages_allowed = 5
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
        print(checksum)
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

    def retrieve_all_sensordata(self):
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

        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_2, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.HUMIDITY_SENSOR_2])
        self.command_queue.put((Order.CHECKSUM, checksum))

        self.command_queue.put((Order.START_BYTE, -1, -1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_3, -1))
        checksum = generate_checksum([Order.REQUEST_SENSOR.value, self.HUMIDITY_SENSOR_3])
        self.command_queue.put((Order.CHECKSUM, checksum, -1))

        # Humidity sensor 4,5,6 should be added in the real system.

    def daily_water(self):
        for i in range(0, 6):
            type = garden[i]["type"]
            if (type > 0) and (garden[i]["humiditysensor value"] <  plants[type]["humidity threshold max"]):
                water_quantity = plants[type]["water quantity"]
                garden[i]["water"] = water_quantity

    def evaluate_sensor_values(self):
        for i in range(0,5):
            quantity=0
            if garden[i]["type"]>0 and sensor_values["airhumidity value"] < self.air_humidity_threshold :
                if garden[i]["humiditysensor value"] < plants[garden[i]["type"]]["humidity threshold min"]:
                    quantity = plants[garden[i]["type"]]["water quantity"]
                if sensor_values["temperature value"] > self.temperature_threshold and sensor_values["lightsensor value"] > self.light_intensity_threshold:
                    quantity += (plants[garden[i]["type"]]["water quantity"])/2;
            if quantity > 0:
                self.water_plant(garden[i]["angle"], quantity)


    def run(self):
        web = False
        while True:
            schedule.every(10).minutes.do(self.retrieve_all_sensordata)
            schedule.every().day.at("12:00").do(self.daily_water)

            #self.evaluate_sensor_values()

            # TODO: hente ting fra nett: legge inn nye planter i hagen vanningsordre
            # TODO: sende data til nett

            if self.test:
                self.water_plant(0,10)
                self.test=False

            #for i in range(0, 6):
            #    if garden[i]["water"] > 0:
            #        self.water_plant(garden[i]["angle"], garden[i]["water"])
            #        garden[i]["water"] = 0

            if (web == True):
                x = 1

        # schedule.every(10).minutes.do(job)
        # schedule.every().hour.do(job)
        # schedule.every().day.at("10:30").do(job)
        # schedule.every(5).to(10).minutes.do(job)
        # schedule.every().monday.do(job)
        # schedule.every().wednesday.at("13:15").do(job)
        # schedule.every().minute.at(":17").do(job)

        # End the threads
        self.exit_event.set()
        self.n_received_tokens.release()

        print("Exiting...")

        for t in self.threads:
            t.join()


def main():
    wp = WaterProgram()
    wp.run()


if __name__ == "__main__":
    main()
