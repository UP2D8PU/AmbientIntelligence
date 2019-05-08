


#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include "queue.h"
#include "devices.h"
#include <DHT.h>

#define _COM_TASK_


/* includes globais */

/* includes globais do compilador WinAVR */

#include <avr/io.h>


/* includes específicos deste módulo */

#include "comm.h"



/* ::define **/


/* Variables **/

uint8_t COM_timer;  /* 10 ms */
uint8_t BYTE_timer;  /* 10 ms */
QueueArray <int8_t> angle_queue = 0; //Unit: degrees
QueueArray <int8_t> water_quantity_queue = 0; //Unit:liters
uint8_t checksum;
bool message_received;
bool is_connected;


/* Functions for init**/
void write_order(enum Order order);
void COM_task(void);
void wait_for_bytes(int num_bytes, uint8_t timeout);



#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
/* Inicialização da tarefa SYS.
  +------------------------------------------------------------------------*/
void /**/COM_init(void)
{
  Serial.begin(9600);
  dht.begin();
  pinMode(LIGHT_SENSOR, INPUT);
  pinMode(HUMIDITY_SENSOR_1, INPUT);

  bool is_connected = false;
  while (!is_connected)
  {
    write_order(HELLO);
    wait_for_bytes(1, 100);
    COM_task();
  }

}



/* Tarefa SYS. Apenas controla o led "alive".
  +------------------------------------------------------------------------*/


void wait_for_bytes(int num_bytes, uint8_t timeout)
{
  uint8_t startTime = BYTE_timer;
  //Wait for incoming bytes or exit if timeout
  while ((Serial.available() < num_bytes) && (BYTE_timer - startTime < timeout)) {}
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

float read_float() {}

//uint8_t is an unsigned 8 bit integer, uint8_t* is a pointer to an 8 bit integer in ram/memory
//The & in front of the pointer type variable will show the actual data held by the pointer.
void write_order(int myOrder) {
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


void write_startbyte()
{
  write_order(START_BYTE);
}

void write_checksum(uint8_t checksum)
{
  write_i8(checksum);
}

void write_order(enum Order order)
{
  uint8_t* Order = (uint8_t*) &order;
  Serial.write(Order, sizeof(uint8_t));
}

void COM_task(void)
{
  Order read_order(void);
  if (Serial.available() > 0) {

    uint8_t checksum = 0 ;
    Order order_received = read_order();

    if (order_received == HELLO) {
      // If the cards haven't say hello, check the connection
      if (!is_connected)
      {
        is_connected = true;
        write_order(HELLO);
      }
      else
      {
        // If we are already connected do not send "hello" to avoid infinite loop
        write_order(ALREADY_CONNECTED);
      }
    }
    else if (order_received == ALREADY_CONNECTED) {
      is_connected = true;
    } else {
      if (order_received == START_BYTE) {
        checksum = START_BYTE;
        Order order = read_order();
        checksum = checksum + order;
        switch (order) {
          case REQUEST_SENSOR:
            {
              int8_t sensor = read_i8();
              checksum = checksum + sensor;
              int16_t received_checksum = read_i16();

              write_startbyte();
              write_order(RECEIVED);
              int16_t checksum_received_message = (START_BYTE + RECEIVED);
              write_checksum(checksum_received_message);

              if (checksum - received_checksum == 0) {
                int msg = 10000;
                if (sensor == TEMPERATURE_SENSOR) {
                  float t = dht.readTemperature();
                  int msg = (int)(t * 10);
                  if (isnan(msg)) {
                    //Print error
                    return;
                  }
                } else if (sensor == AIRHUMIDITY_SENSOR) {
                  float h = dht.readHumidity();
                  int msg = (int)(h * 10);
                  if (isnan(msg)) {
                    //Print error
                    return;
                  }
                } else if (sensor == LIGHT_SENSOR) {
                  int msg = analogRead(LIGHT_SENSOR);
                } else if (sensor == HUMIDITY_SENSOR_1 || sensor == HUMIDITY_SENSOR_2 || sensor == HUMIDITY_SENSOR_3 || sensor == HUMIDITY_SENSOR_4 || sensor == HUMIDITY_SENSOR_5 || sensor == HUMIDITY_SENSOR_6) {
                  int msg = digitalRead(sensor);
                }
                if (msg != 10000) {
                  write_startbyte();
                  write_order(SENSOR_MSG);
                  write_i8(sensor);
                  write_i16(msg);
                  checksum = (START_BYTE + SENSOR_MSG + sensor + msg);
                  write_checksum(checksum);
                } else {
                  write_order(ERROR);
                  write_i16(404);
                  return;
                }
              }
            
            break;
        }

      case ACTION_WATER_PLANT:
        {
          uint8_t plant, amount;
          plant = read_i8();
          amount = read_i8();
          checksum = checksum + plant + amount;
          int8_t received_checksum = read_i16();
          if (received_checksum - checksum == 0) {
            angle_queue.push(plant);
            water_quantity_queue.push(amount);
            write_startbyte();
            write_order(RECEIVED);
            checksum = (START_BYTE + RECEIVED);
            write_checksum(checksum);
          }
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
}
