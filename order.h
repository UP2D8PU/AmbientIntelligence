#ifndef ORDER_H
#define ORDER_H



enum Order {
  HELLO = 10,
  ALREADY_CONNECTED = 1,
  ERROR = 2,
  RECEIVED = 3,
  CHECKSUM = 4,
  REQUEST_SENSOR = 5,
  SENSOR_MSG = 6,
  ACTION_WATER_PLANT = 7,

  START_BYTE = 120,
  
};

typedef enum Order Order;

#endif
