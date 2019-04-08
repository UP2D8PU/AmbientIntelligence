from enum import Enum
import struct
import threading
import time
import schedule

from threads import * #CommandThread, ListenerThread
from utilities import *#CustomQueue, open_serial_port
from database import *#plants, garden


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
            sensor = read_i8(f)
            sensor_data = read_i8(f)
            msg = "sensormsg {}".format(sensor_data)
            if sensor == 0:
                WaterProgram.temperatur_value = sensor_data
            elif sensor == 1:
                WaterProgram.airhumidity_value = sensor_data
            elif sensor == 2:
                WaterProgram.lightsensor_value = sensor_data
            elif sensor == 3:
                WaterProgram.humiditysensor_value[0] = sensor_data
            elif sensor == 4:
                WaterProgram.humiditysensor_value[1] = sensor_data
            elif sensor == 5:
                WaterProgram.humiditysensor_value[2] = sensor_data
            elif sensor == 6:
                WaterProgram.humiditysensor_value[3] = sensor_data
            elif sensor == 7:
                WaterProgram.humiditysensor_value[4] = sensor_data
            elif sensor == 8:
                WaterProgram.humiditysensor_value[5] = sensor_data
            elif sensor == 9:
                WaterProgram.humiditysensor_value[6] = sensor_data
            else:
                msg=""
                print("Unknown Sensor",sensor)

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


class WaterProgram(object):
    def __init__(self):
        self.TEMPERATURE_SENSOR = 0
        self.AIRHUMIDITY_SENSOR=1
        self.LIGHT_SENSOR = 2
        self.HUMIDITY_SENSOR_1=3
        self.HUMIDITY_SENSOR_2=4
        self.HUMIDITY_SENSOR_3=5

        self.temperatur_value = 0
        self.airhumidity_value=0
        self.lightsensor_value=0
        self.humiditysensor_value = [0,0,0,0,0,0,0]



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


        self.command_queue = CustomQueue(6)
        self.n_messages_allowed = 3
        self.n_received_tokens = threading.Semaphore(self.n_messages_allowed)
        self.serial_lock = threading.Lock()
        self.exit_event = threading.Event()

        print("Starting Communication Threads")


        self.threads = [CommandThread(ser, self.command_queue, self.exit_event, self.n_received_tokens, self.serial_lock),
                   ListenerThread(ser, self.exit_event, self.n_received_tokens, self.serial_lock)]
        for t in self.threads:
            t.start()

    def water_plant(self, angle, quantity):
            self.command_queue.put((Order.ACTION_WATER_PLANT, angle))
            self.command_queue.put((Order.ACTION_WATER_QUANTITY, quantity))

    def retrieve_all_sensordata(self):

        self.command_queue.put((Order.REQUEST_SENSOR, self.TEMPERATURE_SENSOR))
        self.command_queue.put((Order.REQUEST_SENSOR, self.AIRHUMIDITY_SENSOR))
        self.command_queue.put((Order.REQUEST_SENSOR, self.LIGHT_SENSOR))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_1))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_2))
        self.command_queue.put((Order.REQUEST_SENSOR, self.HUMIDITY_SENSOR_3))


    def daily_water(self):
        for i in range(0, 6):
            type = garden[i]["type"]
            if type > 0:
                water_quantity = plants[type]["water quantity"]
                garden[i]["water"] = water_quantity

    def evaluate_sensor_values(self):
        for i in range(0, 6):
            if self.plantList[i] > 0:
                soil_threshold = plants[self.plantList[i]]["humidity threshold"]
                water_quantity = plants[self.plantList[i]]["water quantity"]
                light_intensity = plants[self.plantList[i]]["light intensity"]
                if self.humiditysensor_value[i] < soil_threshold:
                    self.wateringList.insert(i,water_quantity)
                if self.humiditysensor_value[i] > soil_threshold+20:
                    self.wateringList.insert(i,0)


                # TODO: FINISH DENNE, oppdater etter garden elementer



    def run(self):
        web = False
        while True:
            schedule.every(1).minutes.do(self.retrieve_all_sensordata())
            schedule.every().day.at("12:00").do(self.daily_water)

            self.evaluate_sensor_values()

        # TODO: hente ting fra nett: legge inn nye planter i hagen vanningsordre
        # TODO: sende data til nett

            if(web == True):
                x=1

            for i in range(0,6):
                if garden[i]["water"] > 0:
                    self.water_plant(garden[i]["angle"],garden[i]["water"])
                    garden[i]["water"]=0











        #schedule.every(10).minutes.do(job)
        #schedule.every().hour.do(job)
        #schedule.every().day.at("10:30").do(job)
        #schedule.every(5).to(10).minutes.do(job)
        #schedule.every().monday.do(job)
        #schedule.every().wednesday.at("13:15").do(job)
        #schedule.every().minute.at(":17").do(job)


        # End the threads
        self.exit_event.set()
        self.n_received_tokens.release()

        print("Exiting...")

        for t in self.threads:
            t.join()





if __name__ =="__main__":
    main = WaterProgram()
    main.run()
