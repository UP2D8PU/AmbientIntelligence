#ifndef _WATER_TASK_
/* ::extern vars **/

extern uint8_t WATER_timer;  /* 10 ms */
#define flow_rate 0.18927; //Average flow rate kitchen sink: 3gpm (gallons per minute) = 0.18927 liters/seconds

/* public functions **/

void WATER_init(void);
void UPDATE_motor(uint8_t angle);
void WATER_task(void);

#endif
