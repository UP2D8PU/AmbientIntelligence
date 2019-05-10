
#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include <avr/io.h>

#include "QueueArray.h"
#include "Servo.h"
#include "devices.h"
#include "comm.h"
#include "var_types.h"

#ifndef _WATER_TASK_
/* ::extern vars **/

//extern uint8 WATER_timer;  /* 10 ms */


/* public functions **/

void WATER_init(void);
void UPDATE_motor(uint8_t angle);
void WATER_task(void);
void timeout_milliseconds(unsigned long timeout);

#endif
