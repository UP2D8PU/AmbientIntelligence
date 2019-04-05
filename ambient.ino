#include "order.h"
#include "devices.h"
#include <Servo.h>

int8_t plant = 0;
int8_t water = 0;
Servo servo;

void setup() {
  Serial.begin(9600);
  
  // Set output pins
  pinMode(WATERPUMP, OUTPUT);
  digitalWrite(WATERPUMP, LOW);
  servo.attach(STEPPERMOTOR);
  
  bool is_connected = true;
  while (!is_connected)
  {
    write_order(HELLO);
    wait_for_bytes(1, 1000);
    comm_task();
  }

}

void loop() {
  comm_task();
  water_plant();


  // servo.write(45); Turn Servo Left to 45 degrees Angir grad, orientation, ikke rotasjon
  // servo.write(90);  Turn Servo back to center position (90 degrees)
  // servo.write(135); Turn Servo Right to 135 degrees
}

void comm_task() {
  if (Serial.available() > 0) {
    Order order = read_order();
    if (order == HELLO) {
      //Ta stilling til oppkobling
    } else {
      switch (order) {
        case REQUEST_SENSOR:
          {
            write_order(RECEIVED);
            int8_t sensor = read_i8();
            if (sensor > 0) {
              int8_t msg = analogRead(sensor);
              write_order(SENSOR_MSG);
              write_i8(msg);
            }
            break;
          }
        case ACTION_WATER_PLANT:
          {
            write_order(RECEIVED);
            plant = read_i8();
            break;
          }
        case ACTION_WATER_PUMP:
          {
            write_order(RECEIVED);
            water = read_i8();
            break;
          }
        default:
          write_order(ERROR);
          write_i16(404);
          return;
      }
    }
  }
}

void wait_for_bytes(int num_bytes, unsigned long timeout)
{
  unsigned long startTime = millis();
  //Wait for incoming bytes or exit if timeout
  while ((Serial.available() < num_bytes) && (millis() - startTime < timeout)) {}
}

Order read_order() {
  return (Order) Serial.read();
}

int8_t read_i8() {
  wait_for_bytes(1, 100); // Wait for 1 byte with a timeout of 100 ms
  return (int8_t) Serial.read();
}

//Not understanding this
int16_t read_i16()
{

}

//uint8_t is an unsigned 8 bit integer, uint8_t* is a pointer to an 8 bit integer in ram/memory
//The & in front of the pointer type variable will show the actual data held by the pointer.
void write_order(enum Order myOrder) {
  uint8_t* Order = (uint8_t*) &myOrder;
  Serial.write(Order, sizeof(uint8_t));
}

void write_i8(int8_t num) {
  Serial.write(num);
}

//Not understanding this
void write_i16(int16_t num)
{
  int8_t buffer[2] = {(int8_t) (num & 0xff), (int8_t) (num >> 8)};
  Serial.write((uint8_t*)&buffer, 2 * sizeof(int8_t));
}

void water_plant() {
  if (plant > 0 && water > 0) {
    //Water
  }
  plant = 0;
  water = 0;
}

}
