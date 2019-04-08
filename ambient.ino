#include "order.h"
#include "QueueArray.h"

float flow_rate = 0.18927; //Average flow rate kitchen sink: 3gpm (gallons per minute) = 0.18927 liters/seconds

QueueArray <int8_t> angle;
QueueArray <int8_t> water_quantity; //Unit:liters

Servo servo;

void setup() {
  Serial.begin(9600);
  bool is_connected = true;
  while (!is_connected)
  { 
    write_order(HELLO);
    wait_for_bytes(1, 1000);
    comm_task();
  }

  TIME_init();
  SYS_init();
  Timer COMM_timer = 0;
  Timer WATER_PLANT_timer = 0; 

}

void loop() {
  TIME_task();
  SYS_task();
  
  COMM_timer++; //per sekund
  WATER_PLANT_timer++;
  //comm_task();
  //water_plant();
}

void comm_task() {
  if (Serial.available() > 0) {
    Order order = read_order();
    if (order == HELLO) {
      //Ta stilling til oppkobling
    } else {
      switch (order) {
        case REQUEST_SENSOR:
          {
            write_order(RECEIVED);
            int8_t sensor = read_i8();
            if (sensor >= 0 && sensor <=5) {
              int8_t msg = analogRead(sensor);
              write_order(SENSOR_MSG);
              write_i8(sensor);
              write_i8(msg);
            }
            break;
          }
        case ACTION_WATER_PLANT:
          {
            write_order(RECEIVED);
            input = read_i8();
            angle.push(input);
            break;
          }
        case ACTION_WATER_QUANTITY:
          {
            write_order(RECEIVED);
            input = read_float();
            water_quantity.push(input);
            break;
          }
        default:
          write_order(ERROR);
          write_i16(404);
          return;
      }
    }
  }
}

void wait_for_bytes(int num_bytes, unsigned long timeout)
{
  unsigned long startTime = millis();
  //Wait for incoming bytes or exit if timeout
  while ((Serial.available() < num_bytes) && (millis() - startTime < timeout)) {}
}

Order read_order() {
  return (Order) Serial.read();
}

int8_t read_i8() {
  wait_for_bytes(1, 100); // Wait for 1 byte with a timeout of 100 ms
  return (int8_t) Serial.read();
}

//Not understanding this
int16_t read_i16()
{
}
float read_float(){}

//uint8_t is an unsigned 8 bit integer, uint8_t* is a pointer to an 8 bit integer in ram/memory
//The & in front of the pointer type variable will show the actual data held by the pointer.
void write_order(enum Order myOrder) {
  uint8_t* Order = (uint8_t*) &myOrder;
  Serial.write(Order, sizeof(uint8_t));
}

void write_i8(int8_t num) {
  Serial.write(num);
}

//Not understanding this
void write_i16(int16_t num)
{
  int8_t buffer[2] = {(int8_t) (num & 0xff), (int8_t) (num >> 8)};
  Serial.write((uint8_t*)&buffer, 2 * sizeof(int8_t));
}

void water_plant() {
  if (angle.count()>0 && water_quantity.count() > 0) {
    //NEED TO HANDLDE TIME
    a=angle.pop();
    q=water_quantity.pop();
    update_motor(a);
    delay(10);     
    int duration = q/flow_rate;
    digitalWrite(WATERPUMP, HIGH);
    delay(duration);
    digitalWrite(WATERPUMP, LOW);
    update_motor(MOTOR_INIT);
    
  }
}
void update_motor(angle){
  servo.write(angle)
  }
}
