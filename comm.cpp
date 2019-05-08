


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


/* Variáveis globais ::vars **/

uint8_t COM_timer;  /* 10 ms */
uint8_t BYTE_timer;  /* 10 ms */
QueueArray <int8_t> angle_queue = 0; //Unit: degrees
QueueArray <int8_t> water_quantity_queue = 0; //Unit:liters
uint8_t checksum;
bool message_received;



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
#if 0
  bool is_connected = true;
  while (!is_connected)
  {
    write_order(HELLO);
    wait_for_bytes(1, 100);
    COM_task();
  }
#endif

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



void COM_task(void)
{
  Order read_order(void);
  if (Serial.available() > 0) {

    uint8_t checksum = 0 ;
    uint8_t start = read_i8();
    if (start - START_BYTE == 0) {
      checksum = start;
      Order order = read_order();

      if (order == HELLO) {
        //Ta stilling til oppkobling
        checksum = (checksum + order);
      } else {
        switch (order) {
            checksum = checksum + order;

          case REQUEST_SENSOR:
            {
              write_startbyte();
              write_order(RECEIVED);
              checksum = (START_BYTE + RECEIVED);
              write_checksum(checksum);
              int8_t sensor = read_i8();
              if (sensor >= 0 && sensor <= 5) {
                checksum = checksum + sensor;
                int8_t received_checksum = read_i8();
                if (received_checksum - checksum == 0) {
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
              }
              break;
            }

          case ACTION_WATER_PLANT:
            {
              uint8_t plant, amount;
              plant = read_i8();
              amount = read_i8();
              checksum = checksum + plant + amount;
              int8_t received_checksum = read_i8();
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
