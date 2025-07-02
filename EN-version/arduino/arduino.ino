#include <Servo.h>

// Pin definitions
const int servoPin = 9;
const int pumpRelayPin = 3;
const int motorRelayPin = 5;
const int lightPins[] = {6, 7, 8, 10, 11};
const int strobePins[] = {12, 13};

// Strobe settings
const long strobeInterval = 100;
bool strobeActive = false;
unsigned long strobeLastMillis = 0;

// Automatic mode
bool isAutomaticMode = false;
unsigned long autoLastMillis = 0;
const long autoInterval = 1000;

Servo servo;
String receivedCommand = ""; // This variable is declared but not used.
bool isPumpOn = false;
bool isMotorOn = false;
bool isServoActive = false; // Servo state

void setup() {
  Serial.begin(9600);

  servo.attach(servoPin);
  pinMode(pumpRelayPin, OUTPUT);
  pinMode(motorRelayPin, OUTPUT);

  for (int i = 0; i < 5; i++) {
    pinMode(lightPins[i], OUTPUT);
  }
  for (int i = 0; i < 2; i++) {
    pinMode(strobePins[i], OUTPUT);
  }

  // Initial state setup
  servo.write(50);    // Neutral initial position
  isServoActive = false; // Servo is inactive initially
  digitalWrite(pumpRelayPin, HIGH); // Assuming HIGH means off for relays
  digitalWrite(motorRelayPin, HIGH); // Assuming HIGH means off for relays

  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], HIGH); // Assuming HIGH means off for lights
  }
  for (int i = 0; i < 2; i++) {
    digitalWrite(strobePins[i], HIGH); // Assuming HIGH means off for strobe lights
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace
    handleCommand(command);
  }

  if (strobeActive) {
    lightEffectStrobe();
  }

  if (isAutomaticMode && !strobeActive) {
    runAutomaticMode();
  }

  delay(10);
}

// Command handling
void handleCommand(String command) {
  if (command == "TEST") {
    Serial.println("OK"); // Respond to test command
  } else if (command == "PUMP_ON") {
    digitalWrite(pumpRelayPin, LOW); // Assuming LOW activates the relay
    isPumpOn = true;
    Serial.println("Pump turned on");
  } else if (command == "PUMP_OFF") {
    digitalWrite(pumpRelayPin, HIGH); // Assuming HIGH deactivates the relay
    isPumpOn = false;
    Serial.println("Pump turned off");
  } else if (command == "SERVO_UP") {
    moveServo(100);
    Serial.println("Servo up");
  } else if (command == "SERVO_DOWN") {
    moveServo(0);
    Serial.println("Servo down");
  } else if (command == "SERVO_STOP") {
    moveServo(50);
    Serial.println("Servo stop");
  } else if (command == "MOTOR_ON") {
    digitalWrite(motorRelayPin, LOW); // Assuming LOW activates the relay
    isMotorOn = true;
    Serial.println("Motor turned on");
  } else if (command == "MOTOR_OFF") {
    digitalWrite(motorRelayPin, HIGH); // Assuming HIGH deactivates the relay
    isMotorOn = false;
    Serial.println("Motor turned off");
  } else if (command == "AUTO_MODE_ON") {
    isAutomaticMode = true;
    Serial.println("Automatic mode activated");
  } else if (command == "AUTO_MODE_OFF") {
    isAutomaticMode = false;
    Serial.println("Automatic mode deactivated");
  } else if (command == "STROBE_ON") {
    strobeActive = true;
    Serial.println("Strobe activated");
  } else if (command == "STROBE_OFF") {
    strobeActive = false;
    stopStrobeEffect();
    if (isAutomaticMode) {
      runAutomaticMode();
    } else {
      resetLights();
    }
    Serial.println("Strobe deactivated");
  }
}

// Function to move the servo
void moveServo(int position) {
  if (isPumpOn) { // The servo can only move if the pump is on
    servo.write(position);
    isServoActive = true;
    delay(500);
  } else {
    Serial.println("Error: The servo cannot move without the pump being on.");
  }
}

// Automatic mode
void runAutomaticMode() {
  unsigned long currentMillis = millis();

  if (currentMillis - autoLastMillis >= autoInterval) {
    autoLastMillis = currentMillis;

    int effect = random(1, 6); // Random number from 1 to 5 (exclusive of 6)
    handleLightEffect(String(effect));
  }
}

// Light effects
void handleLightEffect(String effect) {
  // Turn all lights off before applying new effect (assuming LOW is on)
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], HIGH);
  }

  if (effect == "1") {
    lightEffectPolice();
  } else if (effect == "2") {
    lightEffectAlternating();
  } else if (effect == "3") {
    lightEffectRain();
  } else if (effect == "4") {
    lightEffectRainbow();
  }
  // Effect "5" is randomly chosen but not handled. Consider adding a case for it.
}

void lightEffectPolice() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], LOW); // Turn on
    delay(100);
    digitalWrite(lightPins[i], HIGH); // Turn off
  }
}

void lightEffectAlternating() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], LOW); // Turn on
    delay(200);
    digitalWrite(lightPins[i], HIGH); // Turn off
  }
}

void lightEffectRain() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], random(0, 2)); // Randomly turn on/off
  }
  delay(200);
}

void lightEffectRainbow() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], LOW); // Turn on
    delay(150);
    digitalWrite(lightPins[i], HIGH); // Turn off
  }
}

// Strobe
void lightEffectStrobe() {
  unsigned long currentMillis = millis();

  if (currentMillis - strobeLastMillis >= strobeInterval) {
    strobeLastMillis = currentMillis;

    for (int i = 0; i < 2; i++) {
      digitalWrite(strobePins[i], !digitalRead(strobePins[i])); // Toggle state
    }
  }
}

void stopStrobeEffect() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(strobePins[i], HIGH); // Turn off strobe lights
  }
}

void resetLights() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], HIGH); // Turn off all regular lights
  }
}