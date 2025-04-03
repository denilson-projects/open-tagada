#include <Servo.h>

// Definizione dei pin
const int servoPin = 9;
const int pumpRelayPin = 3;
const int motorRelayPin = 5;
const int lightPins[] = {6, 7, 8, 10, 11};
const int stroboPins[] = {12, 13};

// Impostazioni per lo strobo
const long strobeInterval = 100;
bool strobeActive = false;
unsigned long strobeLastMillis = 0;

// Modalità automatica
bool isAutomaticMode = false;
unsigned long autoLastMillis = 0;
const long autoInterval = 1000;

Servo servo;
String receivedCommand = "";
bool isPumpOn = false;
bool isMotorOn = false;
bool isServoActive = false; // Stato del servo

void setup() {
  Serial.begin(9600);

  servo.attach(servoPin);
  pinMode(pumpRelayPin, OUTPUT);
  pinMode(motorRelayPin, OUTPUT);

  for (int i = 0; i < 5; i++) {
    pinMode(lightPins[i], OUTPUT);
  }
  for (int i = 0; i < 2; i++) {
    pinMode(stroboPins[i], OUTPUT);
  }

  // Inizializzazione stato
  servo.write(50);  // Posizione iniziale neutra
  isServoActive = false; // Il servo è inattivo inizialmente
  digitalWrite(pumpRelayPin, 1);
  digitalWrite(motorRelayPin, 1);

  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 1);
  }
  for (int i = 0; i < 2; i++) {
    digitalWrite(stroboPins[i], 1);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Rimuove eventuali spazi bianchi
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

// Gestione dei comandi
void handleCommand(String command) {
  if (command == "TEST") {
    Serial.println("OK"); // Risponde al comando di test
  } else if (command == "PUMP_ON") {
    digitalWrite(pumpRelayPin, 0);
    isPumpOn = true;
    Serial.println("Pompa accesa");
  } else if (command == "PUMP_OFF") {
    digitalWrite(pumpRelayPin, 1);
    isPumpOn = false;
    Serial.println("Pompa spenta");
  } else if (command == "SERVO_UP") {
    moveServo(100);
    Serial.println("Servo su");
  } else if (command == "SERVO_DOWN") {
    moveServo(0);
    Serial.println("Servo giù");
  } else if (command == "SERVO_STOP") {
    moveServo(50);
    Serial.println("Servo stop");
  } else if (command == "MOTOR_ON") {
    digitalWrite(motorRelayPin, 0);
    isMotorOn = true;
    Serial.println("Motore acceso");
  } else if (command == "MOTOR_OFF") {
    digitalWrite(motorRelayPin, 1);
    isMotorOn = false;
    Serial.println("Motore spento");
  } else if (command == "AUTO_MODE_ON") {
    isAutomaticMode = true;
    Serial.println("Modalità automatica attivata");
  } else if (command == "AUTO_MODE_OFF") {
    isAutomaticMode = false;
    Serial.println("Modalità automatica disattivata");
  } else if (command == "STROBE_ON") {
    strobeActive = true;
    Serial.println("Strobo attivato");
  } else if (command == "STROBE_OFF") {
    strobeActive = false;
    stopStrobeEffect();
    if (isAutomaticMode) {
      runAutomaticMode();
    } else {
      resetLights();
    }
    Serial.println("Strobo disattivato");
  }
}

// Funzione per muovere il servo
void moveServo(int position) {
  if (isPumpOn) { // Il servo può muoversi solo se la pompa è accesa
    servo.write(position);
    isServoActive = true;
    delay(500);
  } else {
    Serial.println("Errore: Il servo non può muoversi senza la pompa accesa.");
  }
}

// Modalità automatica
void runAutomaticMode() {
  unsigned long currentMillis = millis();

  if (currentMillis - autoLastMillis >= autoInterval) {
    autoLastMillis = currentMillis;

    int effect = random(1, 6);
    handleLightEffect(String(effect));
  }
}

// Effetti di luce
void handleLightEffect(String effect) {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 1);
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
}

void lightEffectPolice() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 0);
    delay(100);
    digitalWrite(lightPins[i], 1);
  }
}

void lightEffectAlternating() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 0);
    delay(200);
    digitalWrite(lightPins[i], 1);
  }
}

void lightEffectRain() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], random(0, 2));
  }
  delay(200);
}

void lightEffectRainbow() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 0);
    delay(150);
    digitalWrite(lightPins[i], 1);
  }
}

// Strobo
void lightEffectStrobe() {
  unsigned long currentMillis = millis();

  if (currentMillis - strobeLastMillis >= strobeInterval) {
    strobeLastMillis = currentMillis;

    for (int i = 0; i < 2; i++) {
      digitalWrite(stroboPins[i], !digitalRead(stroboPins[i]));
    }
  }
}

void stopStrobeEffect() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(stroboPins[i], 1);
  }
}

void resetLights() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(lightPins[i], 1);
  }
}
