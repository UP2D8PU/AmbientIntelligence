#ifndef _WATER_TASK_
/* ::extern vars **/

extern uint8_t WATER_timer;  /* 10 ms */

/* public functions **/

void WATER_init(void);
void UPDATE_motor(uint8_t angle);
void WATER_task(void);

#endif
