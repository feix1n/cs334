/*
   This ESP32 code is created by esp32io.com

   This ESP32 code is released in the public domain

   For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-joystick
*/

#define VRX_PIN 34   // ESP32 pin GPIO39 (ADC3) connected to VRX pin
#define VRY_PIN 35   // ESP32 pin GPIO36 (ADC0) connected to VRY pin
#define SW_PIN 32    // Joystick Switch
#define PUSH_PIN 18  // Momentary Button


int valueX = 0;  // to store the X-axis value
int valueY = 0;  // to store the Y-axis value
const int buttonPin = PUSH_PIN;
const int joystickSW = SW_PIN;
int buttonState = 0;  //status of momentary button
int switchState = 0;  // status of joystick switch

int prevbState = 0;
int prevswState = 0;
int prevx = 0;
int prevy = 0;


void setup() {
  Serial.begin(115200);
  // Set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(joystickSW, INPUT_PULLUP);
}


void loop() {
  // read X and Y analog values
  valueX = analogRead(VRX_PIN);
  valueY = analogRead(VRY_PIN);

  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);
  switchState = digitalRead(joystickSW);

  if (prevbState != buttonState) {
    // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
    if (buttonState == HIGH) {
      // turn LED on:
      Serial.println("Momentary: Off");
    } else {
      Serial.println("Momentary: On");
    }
  }

  if (prevswState != switchState) {
    // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
    if (switchState == HIGH) {
      // turn LED on:
      Serial.println("JoystickSW: Off");
    } else {
      Serial.println("JoystickSW: On");
    }
  }

  // print data to Serial Monitor on Arduino IDE
  if (abs(prevx - valueX) > 300 || abs(prevy - valueY) > 300) {
    Serial.print("x = ");
    Serial.print(valueX);
    Serial.print(", y = ");
    Serial.println(valueY);
  }

  prevx = valueX;
  prevy = valueY;
  prevbState = buttonState;
  prevswState = switchState;
  delay(100);
}
