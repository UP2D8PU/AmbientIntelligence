#include "order.h"
#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */
#include <Arduino.h>
#include "QueueArray.h"
#include "devices.h"
#include <DHT.h>
#include <avr/io.h>

#ifndef _COM_TASK_
/* ::extern vars **/



//extern uint8_t COM_timer;  /* 10 ms */
//extern uint8_t BYTE_timer;

/* public functions **/

void COM_init(void);
void COM_task(void);
void write_startbyte(void);
void write_order(enum Order);
void wait_for_bytes(int, unsigned long);
//void write_i16(int16_t)
//void write_checksum(int16_t)



#endif
