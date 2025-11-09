#include <Stepper.h>
#include <ESP32Servo.h>

const int stepsPerRevolution = 2048;  // change this to fit the number of steps per revolution
const int servoPin = 4;
int posDegrees = 0;

// ULN2003 Motor Driver Pins
#define IN1 19
#define IN2 18
#define IN3 5
#define IN4 17

// initialize the stepper library
Stepper myStepper(stepsPerRevolution, IN1, IN3, IN2, IN4);
Servo servo;

void setup() {
  // set the speed at 5 rpm
  myStepper.setSpeed(10);
  servo.attach(servoPin);
  // initialize the serial port
  Serial.begin(115200);
}

void loop() {
  // step one revolution in one direction:
  Serial.println("clockwise");
  myStepper.step(stepsPerRevolution);
  delay(1000);


  for (int i = 0; i <= 10; i++) {
    posDegrees++;
    servo.write(posDegrees);
    Serial.println(posDegrees);
    delay(20);
  }
}