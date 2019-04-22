


#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include "queue.h"

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
QueueArray <int8_t> angle = 0; //Unit: degrees
QueueArray <int8_t> water_quantity = 0; //Unit:liters




/* Inicialização da tarefa SYS.
+------------------------------------------------------------------------*/
void /**/COM_init(void)
{
 Serial.begin(9600);
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
float read_float(){}

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

void /**/COM_task(void)
{
  Order read_order(void);
  
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
            if (sensor >= 0 && sensor <=5) {
              int8_t msg = analogRead(sensor);
              write_order(SENSOR_MSG);
              write_i8(sensor);
              write_i8(msg);
            }
            break;
          }
        case ACTION_WATER_PLANT:
          {
            int8_t input;
            write_order(RECEIVED);
            input = read_i8();
            angle.push(input);
            break;
          }
        case ACTION_WATER_QUANTITY:
          {
            int8_t input;
            write_order(RECEIVED);
            input = read_i8();
            water_quantity.push(input);
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
