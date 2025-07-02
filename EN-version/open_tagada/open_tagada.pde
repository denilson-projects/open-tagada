import processing.serial.*;

// Global variables
Serial arduino;
boolean arduinoConnected = false;
boolean motorState = false;
String lightMode = "Manual"; // Changed from "Manuale"
boolean pistonsRelayState = false;
boolean emergencyMode = false;

// UI variables
ArrayList<String> availablePorts;
int selectedPortIndex = -1;
Button connectButton, disconnectButton, scanButton;
Button pistonButton, jumpButton, motorButton, emergencyButton;
Button strobeButton, lightModeButton;

void setup() {
  size(1200, 800);
  background(40);
  textAlign(CENTER, CENTER);

  // Initialize buttons
  initializeButtons();

  // Scan ports on startup
  scanPorts();
}

void draw() {
  background(40);

  // Draw the interface
  drawInterface();

  // Update button states
  updateButtons();
}

void initializeButtons() {
  // Connection buttons
  scanButton = new Button("Detect Ports", width/2 - 300, 100, 200, 50); // Changed label
  connectButton = new Button("Connect", width/2 - 100, 100, 200, 50); // Changed label
  disconnectButton = new Button("Disconnect", width/2 + 100, 100, 200, 50); // Changed label

  // Control buttons
  pistonButton = new Button("Pistons: OFF", 200, 300, 250, 60); // Changed label
  jumpButton = new Button("JUMP", 200, 380, 250, 60); // Changed label
  motorButton = new Button("Motor: OFF", 200, 460, 250, 60); // Changed label
  emergencyButton = new Button("EMERGENCY STOP", 200, 540, 250, 60); // Changed label

  // Light buttons
  strobeButton = new Button("STROBE", width - 450, 300, 250, 60); // Changed label
  lightModeButton = new Button("Effects: OFF", width - 450, 380, 250, 60); // Changed label
}

void drawInterface() {
  // Titles
  fill(255);
  textSize(32);
  text("Tagadà Control Panel", width/2, 50); // Changed title

  // Connection status
  textSize(20);
  text("Status: " + (arduinoConnected ? "Connected" : "Disconnected"), width/2, 180); // Changed status text

  // Port list
  if (availablePorts != null && availablePorts.size() > 0) {
    textSize(16);
    text("Available Ports:", width/2, 220); // Changed label
    for (int i = 0; i < availablePorts.size(); i++) {
      fill(selectedPortIndex == i ? color(100, 200, 255) : color(255));
      text(availablePorts.get(i), width/2, 250 + i * 25);
    }
  }

  // Draw all buttons
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
  // Handle button clicks
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

  // Port selection
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
      println("Connection error: " + e.getMessage()); // Changed error message
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
    println("Sent command: " + command); // Changed message
  } else {
    println("[Offline] Simulated command: " + command); // Changed message
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
  // sendCommand("SERVO_RESET"); // This command does not exist in the Arduino code
}

void togglePistonsRelay() {
  pistonsRelayState = !pistonsRelayState;
  if (pistonsRelayState) {
    sendCommand("PUMP_ON");
    pistonButton.label = "Pistons: ON"; // Changed label
    jumpButton.enabled = true;
  } else {
    sendCommand("PUMP_OFF");
    // sendCommand("SERVO_RESET"); // This command does not exist in the Arduino code
    pistonButton.label = "Pistons: OFF"; // Changed label
    jumpButton.enabled = false;
  }
}

void toggleMotor() {
  motorState = !motorState;
  if (motorState) {
    sendCommand("MOTOR_ON");
    motorButton.label = "Motor: ON"; // Changed label
  } else {
    sendCommand("MOTOR_OFF");
    motorButton.label = "Motor: OFF"; // Changed label
  }
}

void pressStrobeEffect() {
  sendCommand("STROBE_ON");
}

void releaseStrobeEffect() {
  sendCommand("STROBE_OFF");
}

void toggleLightMode() {
  if (lightMode.equals("Manual")) { // Changed string
    lightMode = "Automatic"; // Changed string
    sendCommand("AUTO_MODE_ON");
    lightModeButton.label = "Effects: ON"; // Changed label
  } else {
    lightMode = "Manual"; // Changed string
    sendCommand("AUTO_MODE_OFF");
    lightModeButton.label = "Effects: OFF"; // Changed label
  }
}

void emergencyStop() {
  emergencyMode = !emergencyMode;
  if (emergencyMode) {
    sendCommand("MOTOR_OFF");
    sendCommand("PUMP_OFF");
    // sendCommand("SERVO_RESET"); // This command does not exist in the Arduino code
    sendCommand("STROBE_OFF");
    sendCommand("AUTO_MODE_OFF");
    motorState = false;
    pistonsRelayState = false;
    lightMode = "Manual"; // Changed string
    motorButton.label = "Motor: OFF"; // Changed label
    pistonButton.label = "Pistons: OFF"; // Changed label
    jumpButton.enabled = false;
    lightModeButton.label = "Effects: OFF"; // Changed label
    emergencyButton.label = "Emergency Reset"; // Changed label
    emergencyButton.backgroundColor = color(0, 255, 0);
  } else {
    emergencyButton.label = "EMERGENCY STOP"; // Changed label
    emergencyButton.backgroundColor = color(255, 0, 0);
  }
}

void updateButtons() {
  jumpButton.enabled = pistonsRelayState && !emergencyMode;
  emergencyButton.backgroundColor = emergencyMode ? color(0, 255, 0) : color(255, 0, 0);
}

// Button class
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
