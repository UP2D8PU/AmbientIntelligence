/* Include **/

#include "water.h"

/* Define **/

#define _WATER_TASK_
#define WATER_STATE_OFF 0 
#define WATER_STATE_ON 1



/* Variables **/
float flow_rate = 0.025; //Average flow 0.025 ml/ms
int MOTOR_INIT = 90; //Initial position of the motor 90 degrees
//uint8_t WATER_timer;
Servo servoMain;
extern QueueArray <uint8_t> angle_queue;
extern QueueArray <uint16_t> water_quantity_queue;
unsigned long MOTOR_TIMEOUT = 500;
int water_state; // waterState used to set the Watering
unsigned long previousMillis; // will store last time water_state was updated
uint8_t angle = 0;
uint16_t quantity = 0;
float duration;

void /**/WATER_init(void)
{
  pinMode(WATERPUMP, OUTPUT);
  servoMain.attach(STEPPERMOTOR);
  update_motor(MOTOR_INIT);
  timeout_milliseconds(MOTOR_TIMEOUT);
  water_state = WATER_STATE_OFF; 
  
}

void update_motor(uint8_t angle)
{
  servoMain.write(angle);
}

void /**/WATER_task(void) {

    // code that needs to be running all the time.
 
  // check to see if it's time to water; that is, if the 
  // difference between the current time and last time you blinked 
  // the LED is bigger than the interval at which you want to 
  // blink the LED.
  if ((water_state == WATER_STATE_OFF) && (angle_queue.count() > 0) && (water_quantity_queue.count() > 0)) {
    angle = angle_queue.dequeue ();
    quantity = water_quantity_queue.dequeue ();
    update_motor(angle);
    timeout_milliseconds(MOTOR_TIMEOUT);
    duration = (quantity/flow_rate); // in milliseconds
    water_state = WATER_STATE_ON;
    previousMillis = millis();  // Remember the time
    digitalWrite(WATERPUMP, HIGH);
  }

if ((water_state == WATER_STATE_ON) && ( (millis() - previousMillis) >= duration)){
  
    water_state = WATER_STATE_OFF;
    digitalWrite(WATERPUMP, LOW);
    timeout_milliseconds(MOTOR_TIMEOUT);
    update_motor(MOTOR_INIT);
    duration = 0;
    previousMillis = millis();
}
}

void timeout_milliseconds(unsigned long timeout)
{
  unsigned long startTime = millis();
  //Wait for incoming bytes or exit if timeout
  while( (millis() -startTime) < timeout) {
    }
}
