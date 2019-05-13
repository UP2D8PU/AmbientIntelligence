
#include "main_tasks.h"

void setup() {
 
  //TIME_init();
  //SYS_init();
  WATER_init();
  COM_init();
  
}
  
void loop() {
  //TIME_task();
  //SYS_task();
  COM_task();
  WATER_task();
  //SYS_led_num_pulses(2);
  
}
