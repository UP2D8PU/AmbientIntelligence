
#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include "queue.h"
#include "Servo.h"
#include "devices.h"
#include "water.h"
#include <avr/io.h>
#include "comm.h"


//#define _COM_TASK_ 
#define _WATER_TASK_



/* Variáveis globais ::vars **/

uint8_t WATER_timer;  /* 10 ms */
Servo servo;

/* Inicialização da tarefa SYS.
+------------------------------------------------------------------------*/
void /**/WATER_init(void)
{
  
}



/* Tarefa SYS. Apenas controla o led "alive".
+------------------------------------------------------------------------*/


void UPDATE_motor(uint8_t angle)
{
  servo.write(angle);
}

void /**/WATER_task(void){
  if (angle.count()>0 && water_quantity.count() > 0) {
    //NEED TO HANDLDE TIME
    uint8_t a;
    uint8_t q;
    a=angle.pop();
    q=water_quantity.pop();
    UPDATE_motor(a);
    delay(10);     
    uint8_t duration = q/flow_rate;
    digitalWrite(WATERPUMP, HIGH);
    delay(duration);
    digitalWrite(WATERPUMP, LOW);
    UPDATE_motor(MOTOR_INIT);
  }
}
