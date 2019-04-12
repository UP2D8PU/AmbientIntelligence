
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

uint8_t WATER_timer;  /* 10 ms */


/* Inicialização da tarefa SYS.
+------------------------------------------------------------------------*/
void /**/WATER_init(void)
{
  
Servo servo;

}



/* Tarefa SYS. Apenas controla o led "alive".
+------------------------------------------------------------------------*/


void /**/WATER_task(void){
  if (angle.count()>0 && water_quantity.count() > 0) {
    //NEED TO HANDLDE TIME
    int8_t a;
    int8_t q;
    a=angle.pop();
    q=water_quantity.pop();
    update_motor(a);
    delay(10);     
    int duration = q/flow_rate;
    digitalWrite(WATERPUMP, HIGH);
    delay(duration);
    digitalWrite(WATERPUMP, LOW);
    update_motor(MOTOR_INIT);
    
  }
}

void update_motor(angle){
  servo.write(angle)
}
