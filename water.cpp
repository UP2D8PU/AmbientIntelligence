
#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include "QueueArray.h"
#include "Servo.h"
#include "devices.h"
#include "water.h"
#include <avr/io.h>
#include "comm.h"

#define _WATER_TASK_



/* Variáveis globais ::vars **/
int flow_rate = 189; //Average flow rate kitchen sink: 189.27 milliliters/seconds
int MOTOR_INIT= 90; //Initial position of the motor 90 degrees

uint8_t WATER_timer;  /* 10 ms */
Servo servoMain;
extern QueueArray <uint8_t> angle_queue;
extern QueueArray <uint8_t> water_quantity_queue;
/* Inicialização da tarefa SYS.
  +------------------------------------------------------------------------*/
void /**/WATER_init(void)
{
  pinMode(WATERPUMP, OUTPUT);
  servoMain.attach(STEPPERMOTOR);
}

void update_motor(uint8_t angle)
{
  servoMain.write(angle);
}

void /**/WATER_task(void) {
  uint8_t angle;
  uint8_t quantity;
  if (angle_queue.count() > 0 && water_quantity_queue.count() > 0) {
        
    angle = angle_queue.dequeue ();
    quantity = water_quantity_queue.dequeue ();
    update_motor(angle);
    delay(500);
    uint8_t duration = quantity / flow_rate;
    digitalWrite(WATERPUMP, HIGH);
    delay(3000);
    digitalWrite(WATERPUMP, LOW);
    update_motor(MOTOR_INIT);
  }
}
