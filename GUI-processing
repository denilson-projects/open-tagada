import processing.serial.*;

// Variabili globali
Serial arduino;
boolean arduinoConnected = false;
boolean motorState = false;
String lightMode = "Manuale";
boolean pistonsRelayState = false;
boolean emergencyMode = false;

// Variabili UI
ArrayList<String> availablePorts;
int selectedPortIndex = -1;
Button connectButton, disconnectButton, scanButton;
Button pistonButton, jumpButton, motorButton, emergencyButton;
Button strobeButton, lightModeButton;

void setup() {
  size(1200, 800);
  background(40);
  textAlign(CENTER, CENTER);
  
  // Inizializza i pulsanti
  initializeButtons();
  
  // Scansiona le porte all'avvio
  scanPorts();
}

void draw() {
  background(40);
  
  // Disegna l'interfaccia
  drawInterface();
  
  // Aggiorna i pulsanti
  updateButtons();
}

void initializeButtons() {
  // Pulsanti di connessione
  scanButton = new Button("Rileva Porte", width/2 - 300, 100, 200, 50);
  connectButton = new Button("Connetti", width/2 - 100, 100, 200, 50);
  disconnectButton = new Button("Disconnetti", width/2 + 100, 100, 200, 50);
  
  // Pulsanti di controllo
  pistonButton = new Button("Pistoni: OFF", 200, 300, 250, 60);
  jumpButton = new Button("SALTA", 200, 380, 250, 60);
  motorButton = new Button("Motore: OFF", 200, 460, 250, 60);
  emergencyButton = new Button("EMERGENZA STOP", 200, 540, 250, 60);
  
  // Pulsanti luci
  strobeButton = new Button("STROBO", width - 450, 300, 250, 60);
  lightModeButton = new Button("Effetti: OFF", width - 450, 380, 250, 60);
}

void drawInterface() {
  // Titoli
  fill(255);
  textSize(32);
  text("Pannello di controllo Tagadà", width/2, 50);
  
  // Stato connessione
  textSize(20);
  text("Stato: " + (arduinoConnected ? "Connesso" : "Non Connesso"), width/2, 180);
  
  // Lista porte
  if (availablePorts != null && availablePorts.size() > 0) {
    textSize(16);
    text("Porte disponibili:", width/2, 220);
    for (int i = 0; i < availablePorts.size(); i++) {
      fill(selectedPortIndex == i ? color(100, 200, 255) : color(255));
      text(availablePorts.get(i), width/2, 250 + i * 25);
    }
  }
  
  // Disegna tutti i pulsanti
  scanButton.display();
  connectButton.display();
  disconnectButton.display();
  pistonButton.display();
  jumpButton.display();
  motorButton.display();
  emergencyButton.display();
  strobeButton.display();
  lightModeButton.display();
}

void mousePressed() {
  // Gestione click sui pulsanti
  if (scanButton.isMouseOver()) {
    scanPorts();
  } else if (connectButton.isMouseOver()) {
    connectArduino();
  } else if (disconnectButton.isMouseOver()) {
    disconnectArduino();
  } else if (pistonButton.isMouseOver()) {
    togglePistonsRelay();
  } else if (jumpButton.isMouseOver()) {
    moveUp();
  } else if (motorButton.isMouseOver()) {
    toggleMotor();
  } else if (emergencyButton.isMouseOver()) {
    emergencyStop();
  } else if (strobeButton.isMouseOver()) {
    pressStrobeEffect();
  } else if (lightModeButton.isMouseOver()) {
    toggleLightMode();
  }
  
  // Selezione porta
  if (availablePorts != null) {
    for (int i = 0; i < availablePorts.size(); i++) {
      float y = 250 + i * 25;
      if (mouseY > y - 10 && mouseY < y + 10 && mouseX > width/2 - 100 && mouseX < width/2 + 100) {
        selectedPortIndex = i;
        break;
      }
    }
  }
}

void mouseReleased() {
  if (jumpButton.isMouseOver()) {
    stopMoveUp();
  }
  if (strobeButton.isMouseOver()) {
    releaseStrobeEffect();
  }
}

void scanPorts() {
  availablePorts = new ArrayList<String>();
  for (String port : Serial.list()) {
    availablePorts.add(port);
  }
  if (availablePorts.size() > 0) {
    selectedPortIndex = 0;
  }
}

void connectArduino() {
  if (selectedPortIndex >= 0 && selectedPortIndex < availablePorts.size()) {
    try {
      String port = availablePorts.get(selectedPortIndex);
      arduino = new Serial(this, port, 9600);
      delay(2000);
      arduinoConnected = true;
    } catch (Exception e) {
      println("Errore di connessione: " + e.getMessage());
      arduino = null;
      arduinoConnected = false;
    }
  }
}

void disconnectArduino() {
  if (arduino != null) {
    arduino.stop();
  }
  arduino = null;
  arduinoConnected = false;
}

void sendCommand(String command) {
  if (arduino != null) {
    arduino.write(command + "\n");
    println("Inviato comando: " + command);
  } else {
    println("[Offline] Comando simulato: " + command);
  }
}

void moveUp() {
  if (pistonsRelayState) {
    sendCommand("PUMP_ON");
    sendCommand("SERVO_UP");
  }
}

void stopMoveUp() {
  sendCommand("SERVO_DOWN");
  delay(500);
  sendCommand("SERVO_STOP");
  sendCommand("SERVO_RESET");
}

void togglePistonsRelay() {
  pistonsRelayState = !pistonsRelayState;
  if (pistonsRelayState) {
    sendCommand("PUMP_ON");
    pistonButton.label = "Pistoni: ON";
    jumpButton.enabled = true;
  } else {
    sendCommand("PUMP_OFF");
    sendCommand("SERVO_RESET");
    pistonButton.label = "Pistoni: OFF";
    jumpButton.enabled = false;
  }
}

void toggleMotor() {
  motorState = !motorState;
  if (motorState) {
    sendCommand("MOTOR_ON");
    motorButton.label = "Motore: ON";
  } else {
    sendCommand("MOTOR_OFF");
    motorButton.label = "Motore: OFF";
  }
}

void pressStrobeEffect() {
  sendCommand("STROBE_ON");
}

void releaseStrobeEffect() {
  sendCommand("STROBE_OFF");
}

void toggleLightMode() {
  if (lightMode.equals("Manuale")) {
    lightMode = "Automatica";
    sendCommand("AUTO_MODE_ON");
    lightModeButton.label = "Effetti: ON";
  } else {
    lightMode = "Manuale";
    sendCommand("AUTO_MODE_OFF");
    lightModeButton.label = "Effetti: OFF";
  }
}

void emergencyStop() {
  emergencyMode = !emergencyMode;
  if (emergencyMode) {
    sendCommand("MOTOR_OFF");
    sendCommand("PUMP_OFF");
    sendCommand("SERVO_RESET");
    sendCommand("STROBE_OFF");
    sendCommand("AUTO_MODE_OFF");
    motorState = false;
    pistonsRelayState = false;
    lightMode = "Manuale";
    motorButton.label = "Motore: OFF";
    pistonButton.label = "Pistoni: OFF";
    jumpButton.enabled = false;
    lightModeButton.label = "Effetti: OFF";
    emergencyButton.label = "Reset Emergenza";
    emergencyButton.backgroundColor = color(0, 255, 0);
  } else {
    emergencyButton.label = "EMERGENZA STOP";
    emergencyButton.backgroundColor = color(255, 0, 0);
  }
}

void updateButtons() {
  jumpButton.enabled = pistonsRelayState && !emergencyMode;
  emergencyButton.backgroundColor = emergencyMode ? color(0, 255, 0) : color(255, 0, 0);
}

// Classe per i pulsanti
class Button {
  float x, y, w, h;
  String label;
  color backgroundColor;
  boolean enabled;
  
  Button(String label, float x, float y, float w, float h) {
    this.label = label;
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.backgroundColor = color(60, 120, 200);
    this.enabled = true;
  }
  
  void display() {
    pushStyle();
    if (!enabled) {
      fill(100);
    } else if (isMouseOver()) {
      fill(backgroundColor, 200);
    } else {
      fill(backgroundColor);
    }
    stroke(200);
    rect(x, y, w, h, 10);
    
    fill(255);
    textAlign(CENTER, CENTER);
    textSize(16);
    text(label, x + w/2, y + h/2);
    popStyle();
  }
  
  boolean isMouseOver() {
    return enabled && mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
  }
}
