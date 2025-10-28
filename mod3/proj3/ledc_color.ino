
#include <math.h>

#define MAX 4095

const int potPin = 32;
const int buttonPin = 18;
const int photoPin = 35;
const int redPin = 16;
const int greenPin = 17;
const int bluePin = 5;

// PWM channels
const int R = 0;
const int G = 1;
const int B = 2;

// button state
bool isPaused = false;

int color[3] = { 0, 0, 0 };
int RGB[3] = { 0, 0, 0 };
int HSV[3] = { 0, 0, 0 };
int darkLevel[3] = { 0, 0, 0 };
int lightLevel[3] = { 0, 0, 0 };

void setup() {
  Serial.begin(115200);

  // Configure PWM (built into ESP32 - no library needed!)
  ledcAttach(redPin, 5000, 8);  // 5kHz, 8-bit resolution (0-255)
  ledcAttach(greenPin, 5000, 8);
  ledcAttach(bluePin, 5000, 8);

  pinMode(buttonPin, INPUT_PULLUP);
  delay(5000);
  calibrateSensors();
}

void calibrateSensors() {
  Serial.println("=== CALIBRATION ===");

  // DARK CALIBRATION
  Serial.println("Put BLACK reference and press the button...");
  while (digitalRead(buttonPin) == HIGH) {
    delay(10);  // small debounce
  }
  // Optional: wait for release so it doesn't trigger twice
  while (digitalRead(buttonPin) == LOW) {
    delay(1);
  }
  Serial.println("Reading...");

  ledcWrite(redPin, 30);  // LOW brightness!
  delay(800);
  darkLevel[0] = analogRead(photoPin);
  ledcWrite(redPin, 0);

  ledcWrite(greenPin, 30);
  delay(800);
  darkLevel[1] = analogRead(photoPin);
  ledcWrite(greenPin, 0);

  ledcWrite(bluePin, 30);
  delay(800);
  darkLevel[2] = analogRead(photoPin);
  ledcWrite(bluePin, 0);

  // LIGHT CALIBRATION
  Serial.println("Put WHITE reference and press the button...");
  while (digitalRead(buttonPin) == HIGH) {
    delay(10);  // small debounce
  }
  // Optional: wait for release so it doesn't trigger twice
  while (digitalRead(buttonPin) == LOW) {
    delay(1);
  }
  Serial.print("Reading...");

  ledcWrite(redPin, 30);
  delay(800);
  lightLevel[0] = analogRead(photoPin);
  ledcWrite(redPin, 0);

  ledcWrite(greenPin, 30);
  delay(800);
  lightLevel[1] = analogRead(photoPin);
  ledcWrite(greenPin, 0);

  ledcWrite(bluePin, 30);
  delay(800);
  lightLevel[2] = analogRead(photoPin);
  ledcWrite(bluePin, 0);

  Serial.println("Calibration complete!");
  Serial.print("Dark: R");
  Serial.print(darkLevel[0]);
  Serial.print(" G");
  Serial.print(darkLevel[1]);
  Serial.print(" B");
  Serial.println(darkLevel[2]);
  Serial.print("Light: R");
  Serial.print(lightLevel[0]);
  Serial.print(" G");
  Serial.print(lightLevel[1]);
  Serial.print(" B");
  Serial.println(lightLevel[2]);
}

void loop() {
  detectColor();
  mapColor();

  // if button is pressed, color is selected
  int button = digitalRead(buttonPin);
  if (button == LOW) {
    while (digitalRead(buttonPin) == LOW)
      delay(1);
    isPaused = true;
    Serial.println("Entering pause mode");
  }

  // print out pot adjustments instead
  while (isPaused) {
    int potVal = analogRead(potPin);
    Serial.print("Pot: ");
    delay(100);
    Serial.println(potVal);
    if (digitalRead(buttonPin) == LOW) {
      isPaused = false;
    }
  }
  printStats();
  delay(1000);
}

void printStats() {
  int potValue = analogRead(potPin);  // Val range 0 - 4096
  int buttonVal = digitalRead(buttonPin);

  Serial.println("--- Color Detection ---");
  Serial.print("Raw: ");
  Serial.print(color[0]);
  Serial.print(",");
  Serial.print(color[1]);
  Serial.print(",");
  Serial.println(color[2]);

  Serial.print("Mapped RGB (gamma-corrected): ");
  Serial.print(RGB[0]);
  Serial.print(",");
  Serial.print(RGB[1]);
  Serial.print(",");
  Serial.println(RGB[2]);

  Serial.print("Pot: ");
  Serial.println(potValue);

  Serial.print("Button: ");
  if (buttonVal == HIGH) {
    Serial.println("not pressed");
  } else {
    Serial.println("pressed");
  }
  delay(1000);
}

void detectColor() {
  // Use consistent low brightness
  ledcWrite(redPin, 30);
  delay(500);
  color[0] = analogRead(photoPin);
  ledcWrite(redPin, 0);

  ledcWrite(greenPin, 30);
  delay(500);
  color[1] = analogRead(photoPin);
  ledcWrite(greenPin, 0);

  ledcWrite(bluePin, 30);
  delay(500);
  color[2] = analogRead(photoPin);
  ledcWrite(bluePin, 0);
}


void mapColor() {
  // Map to [0,1] normalized range based on calibration
  float redNorm = (float)(color[0] - darkLevel[0]) / (lightLevel[0] - darkLevel[0]);
  float greenNorm = (float)(color[1] - darkLevel[1]) / (lightLevel[1] - darkLevel[1]);
  float blueNorm = (float)(color[2] - darkLevel[2]) / (lightLevel[2] - darkLevel[2]);

  // Clamp to [0,1]
  redNorm = constrain(redNorm, 0.0, 1.0);
  greenNorm = constrain(greenNorm, 0.0, 1.0);
  blueNorm = constrain(blueNorm, 0.0, 1.0);

  // Apply gamma correction
  float gamma = 2.0;  // tweak between 1.6–2.2 depending on sensor
  redNorm = pow(redNorm, 1.0 / gamma);
  greenNorm = pow(greenNorm, 1.0 / gamma);
  blueNorm = pow(blueNorm, 1.0 / gamma);

  // Convert to 8-bit range
  int redVal = int(redNorm * 255.0);
  int greenVal = int(greenNorm * 255.0);
  int blueVal = int(blueNorm * 255.0);

  // Optional saturation boost for vividness
  float satBoost = 1.2;
  redVal = constrain(int(redVal * satBoost), 0, 255);
  greenVal = constrain(int(greenVal * satBoost), 0, 255);
  blueVal = constrain(int(blueVal * satBoost), 0, 255);

  RGB[0] = redVal;
  RGB[1] = greenVal;
  RGB[2] = blueVal;
}