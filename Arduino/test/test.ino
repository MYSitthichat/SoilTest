// Pin definitions
const int PWM_PIN = 9;   // PWM pin for speed control
const int DIR_PIN = 8;   // Direction control pin

// Speed parameters
const int maxSpeed = 15000;       // Max PWM value for full speed
const int minSpeed = 0;         // Min PWM value
int currentSpeed = 0;           // Current speed
int speedStep = 100;              // Step increment for speed
bool direction = true;          // Direction control

void setup() {
  // Initialize motor control pins
  pinMode(PWM_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  // Start in forward direction
  digitalWrite(DIR_PIN, HIGH);
}

void loop() {
  // Set the PWM speed
  analogWrite(PWM_PIN, currentSpeed);

  // Gradually increase speed until maxSpeed
  currentSpeed += speedStep;

  // If reached maxSpeed, reverse direction
  if (currentSpeed >= maxSpeed) {
    // Reverse the direction
    direction = !direction;
    digitalWrite(DIR_PIN, direction ? HIGH : LOW);

    // Reset the speed to start from minSpeed
    currentSpeed = minSpeed;
  }

  // Small delay to control acceleration rate
  delay(10);
}
