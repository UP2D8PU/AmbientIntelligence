#include "order.h"
#include <stdio.h>
#include <stdint.h> 
#include <Arduino.h>
#include <avr/io.h>

#include "QueueArray.h"
#include "Servo.h"
#include "devices.h"
#include "comm.h"

#ifndef _WATER_TASK_

/* ::extern vars **/
extern float duration;
extern unsigned long previousMillis;
extern int water_state;

/* public functions **/

void WATER_init(void);
void update_motor(uint8_t angle);
void WATER_task(void);
void timeout_milliseconds(unsigned long timeout);

#endif
