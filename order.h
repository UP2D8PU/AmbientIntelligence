#ifndef ORDER_H
#define ORDER_H

// Define the orders that can be sent and received
enum Order {
  HELLO = 0,
  ALREADY_CONNECTED = 1,
  ERROR = 2,
  RECEIVED = 3,
  STOP = 4,

  REQUEST_SENSOR = 5,
  SENSOR_MSG = 6,
  ACTION_WATER_PLANT = 7,
  ACTION_WATER_QUANTITY = 8,
  ACTION_STOP_WATER = 9,
  WATERING_FINISHED = 10;
};

typedef enum Order Order;

#endif
