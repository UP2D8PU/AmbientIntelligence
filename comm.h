#include "order.h"
#ifndef _COM_TASK_
/* ::extern vars **/

extern uint8_t COM_timer;  /* 10 ms */
extern uint8_t BYTE_timer;

/* public functions **/

void COM_init(void);
void COM_task(void);



#endif
