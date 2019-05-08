
#include "main_tasks.h"
#include "devices.h"
#include "queue.h"


// TO DO: Implement communication code med startsum og checksum
void setup() {
 
  TIME_init();
  //SYS_init();
  COM_init();
  WATER_init();
}
  
void loop() {
  TIME_task();
  //SYS_task();
  COM_task();
  WATER_task();
  //SYS_led_num_pulses(2);
}
