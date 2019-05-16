
#include "main_tasks.h"

void setup() {
 
  WATER_init();
  COM_init();
  
}
  
void loop() {

  COM_task();
  WATER_task();
  
}
