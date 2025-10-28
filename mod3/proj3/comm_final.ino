
#include <math.h>
#include <WiFi.h>

const char* ssid = "yale wireless";
const char* host = "10.67.74.186";  // Replace with Pi's IP
const int port = 5000;

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

// setup wifi
WiFiClient client;

void activeDelay(int ms) {
  unsigned long start = millis();
  // Turn LEDs white while waiting
  ledcWrite(redPin, 20);
  ledcWrite(greenPin, 20);
  ledcWrite(bluePin, 20);

  while (millis() - start < ms) {
    delay(10);  // still yields to WiFi stack
  }

  // Turn them off afterward
  ledcWrite(redPin, 0);
  ledcWrite(greenPin, 0);
  ledcWrite(bluePin, 0);
}

void setup() {
  Serial.begin(115200);

  analogReadResolution(12);        
  analogSetAttenuation(ADC_11db);  

  // Configure PWM (built into ESP32 - no library needed!)
  ledcAttach(redPin, 5000, 8);  // 5kHz, 8-bit resolution (0-255)
  ledcAttach(greenPin, 5000, 8);
  ledcAttach(bluePin, 5000, 8);

  analogSetPinAttenuation(potPin, ADC_11db);

  WiFi.begin(ssid);
  Serial.println("\nConnecting");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    activeDelay(100);
  }

  Serial.println("\nConnected to the WiFi network");
  Serial.print("Local ESP32 IP: ");
  Serial.println(WiFi.localIP());

  connectToServer();

  pinMode(buttonPin, INPUT_PULLUP);
  activeDelay(5000);
  calibrateSensors();
}

void connectToServer() {
  if (client.connected()) {
    client.stop();  // Properly close the connection
    delay(1000);    // Give time for cleanup
  }

  while (!client.connected()) {
    Serial.print("Connecting to Raspberry Pi...");
    if (client.connect(host, port)) {
      Serial.println("Connected!");
      client.println("Connected to ESP32!");
    } else {
      Serial.println("Failed, retrying in 2 seconds...");
      activeDelay(2000);
    }
  }
}

void calibrateSensors() {
  Serial.println("=== CALIBRATION ===");

  // DARK CALIBRATION
  Serial.println("Put BLACK reference and press the button...");
  client.println("Put BLACK reference and press the button...");
  while (digitalRead(buttonPin) == HIGH) {
    delay(10);  // small debounce
  }
  // Optional: wait for release so it doesn't trigger twice
  while (digitalRead(buttonPin) == LOW) {
    activeDelay(1);
  }
  Serial.println("Reading...");
  client.println("Reading...");

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
  client.println("Put WHITE reference and press the button...");
  while (digitalRead(buttonPin) == HIGH) {
    delay(10);  // small debounce
  }
  // Optional: wait for release so it doesn't trigger twice
  while (digitalRead(buttonPin) == LOW) {
    activeDelay(1);
  }
  Serial.print("Reading...");
  client.println("Reading...");

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
  client.println("Calibration complete!");
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
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    WiFi.begin(ssid);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print(".");
      delay(500);
    }
  }
  if (!client.connected()) {
    Serial.println("Client disconnected, reconnecting...");
    connectToServer();
  } else {
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
      Serial.println(potVal);
      client.print("Pot: ");
      client.println(potVal);
      activeDelay(300);
      if (digitalRead(buttonPin) == LOW) {
        isPaused = false;
      }
    }
    printStats();
    activeDelay(1000);
  }
}

void printStats() {
  int potValue = analogRead(potPin);  // Val range 0 - 4096
  int buttonVal = digitalRead(buttonPin);

  // Serial.println("--- Color Detection ---");
  // Serial.print("Raw: ");
  // Serial.print(color[0]);
  // Serial.print(",");
  // Serial.print(color[1]);
  // Serial.print(",");
  // Serial.println(color[2]);

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

  // Send to server if connected
  if (client.connected()) {
    client.print("RGB: ");
    client.print(RGB[0]);
    client.print(",");
    client.print(RGB[1]);
    client.print(",");
    client.println(RGB[2]);
  }
}

void detectColor() {
  for (int i = 0; i < 5; i++) analogRead(photoPin);

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