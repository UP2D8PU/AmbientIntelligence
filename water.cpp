/* Include **/

#include "water.h"

/* Define **/

#define _WATER_TASK_



/* Variables **/
int flow_rate = 189; //Average flow rate kitchen sink: 189.27 milliliters/seconds
int MOTOR_INIT = 90; //Initial position of the motor 90 degrees
uint8_t WATER_timer;
Servo servoMain;
extern QueueArray <uint8_t> angle_queue;
extern QueueArray <uint16_t> water_quantity_queue;
unsigned long MOTOR_TIMEOUT = 500;


void /**/WATER_init(void)
{
  pinMode(WATERPUMP, OUTPUT);
  servoMain.attach(STEPPERMOTOR);
}

void update_motor(uint8_t angle)
{
  servoMain.write(angle);
}

void /**/WATER_task(void) {
  uint8_t angle;
  uint16_t quantity;
  if (angle_queue.count() > 0 && water_quantity_queue.count() > 0) {
    angle = angle_queue.dequeue ();
    quantity = water_quantity_queue.dequeue ();
    update_motor(angle);
    timeout_milliseconds(MOTOR_TIMEOUT);
    unsigned long duration = quantity *1000 / flow_rate; // in milliseconds
    digitalWrite(WATERPUMP, HIGH);
    timeout_milliseconds(duration);
    digitalWrite(WATERPUMP, LOW);
    update_motor(MOTOR_INIT);
  }
}

void timeout_milliseconds(unsigned long timeout)
{
  unsigned long startTime = millis();
  //Wait for incoming bytes or exit if timeout
  while( (millis() -startTime) < timeout) {
    }
}
