#include <ESP32Servo.h>
#include <Stepper.h>

// ULN2003 Motor Driver Pins
#define IN1 19
#define IN2 18
#define IN3 5
#define IN4 17

// stepper setup
const int stepsPerRevolution = 1024;
const int quarterTurn = stepsPerRevolution / 4;
Stepper myStepper(stepsPerRevolution, IN1, IN3, IN2, IN4);
bool stepperActive = false;

// photoresistor setup
const int lightPin = 34;
int threshold = 2000;

// servo setup
const int servoPin = 4;
Servo servo;
const unsigned long servoDuration = 10000;
unsigned long servoStart = 0;
bool canRelock = false;
bool servoRaised = false;
bool servoPlayed = false;

// hall effect sensor setup
const int hallPin = 25;
volatile bool hallTriggeredFlag = false;

bool isLocked = true;


void IRAM_ATTR hallISR() {
  // triggers as soon as hall sensor is pulled low
  hallTriggeredFlag = true;
}

void setup() {
  Serial.begin(115200);

  // set up motors
  servo.attach(servoPin);
  myStepper.setSpeed(10);

  // set servo to init position
  servo.write(0);

  pinMode(hallPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(hallPin), hallISR, FALLING);
}

void loop() {
  // Detect magnet to unlock, and unlock box
  if (hallTriggeredFlag && isLocked) {
    Serial.println("MAGNET DETECTED → Unlocking");
    hallTriggeredFlag = false;
    myStepper.step(-512);
    isLocked = false;
    Serial.println("Unlocked.");
  }

  int lightValue = analogRead(lightPin);
  Serial.print("Light: ");
  Serial.println(lightValue);

  // if lock is disengaged, servo should pop up (only once)
  if (!isLocked && !servoRaised && lightValue > threshold && !servoPlayed) {
    Serial.println("Bright → Popping servo up");
    servo.write(115);
    servoStart = millis();
    servoRaised = true;
    canRelock = true;
  }

  // once servo is up for 10 seconds, go back down to rest position
  if (servoRaised && millis() - servoStart >= servoDuration) {
    Serial.println("Servo timeout → Returning down");
    for (int pos = 115; pos >= 15; pos--) {
      servo.write(pos);
      delay(10);
    }
    servoRaised = false;
    servoPlayed = true;
  }

  // once box is closed, reengage locking mechanism
  if (!isLocked && !servoRaised && canRelock && lightValue < threshold) {
    Serial.println("Dark again → Locking");
    myStepper.step(512);
    isLocked = true;
    canRelock = false;
    hallTriggeredFlag = false;
    Serial.println("Locked.");
  }

  delay(10);
}
