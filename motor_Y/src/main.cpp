#include <Arduino.h>

// Motor 1
#define DIR_PIN_1 4
#define STEP_PIN_1 5
#define ENABLE_PIN_1 6
// Switch
#define SWITCH_START_1 A2
#define SWITCH_REVERSE_1 A3

bool isRunning = false;
bool direction = true;
unsigned long speedDelay = 260;
unsigned long lastPulseTime = 0;
bool stepState = false;
String lastCommand = "";

void stopAllMotors();
void handleSerialCommand();
void handleButtonPress();
void controlMotor(int motorIndex, bool state, bool dir);

void setup()
{
    pinMode(DIR_PIN_1, OUTPUT);
    pinMode(STEP_PIN_1, OUTPUT);
    pinMode(ENABLE_PIN_1, OUTPUT);
    pinMode(SWITCH_START_1, INPUT_PULLUP);
    pinMode(SWITCH_REVERSE_1, INPUT_PULLUP);
    digitalWrite(ENABLE_PIN_1, HIGH);

    Serial.begin(9600);
    Serial.println("Setup complete");
}

void loop()
{
    handleSerialCommand();
    handleButtonPress();
    if (isRunning)
    {
      if (micros() - lastPulseTime >= speedDelay)
      {
        lastPulseTime = micros();
        digitalWrite(STEP_PIN_1, HIGH);
        delayMicroseconds(2);
        digitalWrite(STEP_PIN_1, LOW);
      }
    }
    else
    {
      digitalWrite(STEP_PIN_1, LOW);
    }
}

void handleButtonPress()
{
    static unsigned long lastDebounceTimeStart = 0;
    static unsigned long lastDebounceTimeReverse = 0;
    const unsigned long debounceDelay = 50;
    static int lastSwitchStateStart = HIGH;
    static int lastSwitchStateReverse = HIGH;
    static int buttonStateStart = HIGH;
    static int buttonStateReverse = HIGH;
    static unsigned long buttonPressTimeStart = 0;
    static unsigned long buttonPressTimeReverse = 0;

    int currentSwitchStateStart = digitalRead(SWITCH_START_1);
    if (currentSwitchStateStart != lastSwitchStateStart)
    {
        lastDebounceTimeStart = millis();
    }

    if ((millis() - lastDebounceTimeStart) > debounceDelay)
    {
        if (currentSwitchStateStart != buttonStateStart)
        {
            buttonStateStart = currentSwitchStateStart;

            if (buttonStateStart == LOW)
            {
                buttonPressTimeStart = millis();  
            }
            else
            {
                if (millis() - buttonPressTimeStart > debounceDelay) 
                {
                    isRunning = !isRunning;
                    digitalWrite(ENABLE_PIN_1, isRunning ? LOW : HIGH);
                    Serial.print("Motor ");
                    Serial.println(isRunning ? "started" : "stopped");
                }
            }
        }
    }
    lastSwitchStateStart = currentSwitchStateStart;

    int currentSwitchStateReverse = digitalRead(SWITCH_REVERSE_1);
    if (currentSwitchStateReverse != lastSwitchStateReverse)
    {
        lastDebounceTimeReverse = millis();
    }

    if ((millis() - lastDebounceTimeReverse) > debounceDelay)
    {
        if (currentSwitchStateReverse != buttonStateReverse)
        {
            buttonStateReverse = currentSwitchStateReverse;

            if (buttonStateReverse == LOW)
            {
                buttonPressTimeReverse = millis(); 
            }
            else
            {
                if (millis() - buttonPressTimeReverse > debounceDelay) 
                {
                    direction = !direction;
                    digitalWrite(DIR_PIN_1, direction ? HIGH : LOW);
                    Serial.println("Motor direction reversed");
                }
            }
        }
    }
    lastSwitchStateReverse = currentSwitchStateReverse;

    if (buttonStateStart == LOW && millis() - buttonPressTimeStart > debounceDelay)
    {
        isRunning = true;
        digitalWrite(ENABLE_PIN_1, LOW); 
        Serial.println("Motor running...");
    }

    if (buttonStateReverse == LOW && millis() - buttonPressTimeReverse > debounceDelay)
    {
        direction = !direction;
        digitalWrite(DIR_PIN_1, direction ? HIGH : LOW); // เปลี่ยนทิศทางมอเตอร์
        Serial.println("Motor direction reversed");
    }
}

void controlMotor(int motorIndex, bool state, bool dir)
{
    isRunning = state;

    digitalWrite(ENABLE_PIN_1, !state);
    digitalWrite(DIR_PIN_1, dir ? HIGH : LOW);

    Serial.print("Motor ");
    Serial.print(motorIndex + 1);
    Serial.println(state ? " started" : " stopped");
}
void handleSerialCommand()
{
    if (Serial.available())
    {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "stop all")
        {
            stopAllMotors();
            return;
        }

        command.toLowerCase();
        if (command.length() > 5 || command == lastCommand)
            return;
        lastCommand = command;

        if (command.startsWith("p1"))
        {
            int speedLevel = command.substring(2).toInt();

            Serial.print("Received command: ");
            Serial.println(command);
            Serial.print("Extracted Speed Level: ");
            Serial.println(speedLevel);

            if (speedLevel < 0 || speedLevel > 100)
            {
                Serial.println("❌ Invalid Speed Level (ต้องอยู่ระหว่าง 0-100%)");
                return;
            }

            speedDelay = map(speedLevel, 0, 100, 10000, 260);  

            Serial.print("✅ Motor Speed set to ");
            Serial.print(speedLevel);
            Serial.print("% (Mapped delay: ");
            Serial.print(speedDelay);
            Serial.println(" us)");

         if (!isRunning)
        {
          controlMotor(0, true, direction);  
        }
        }
        else if (command == "m1")
        {
            controlMotor(0, true, true);  
        }
        else if (command == "m1r")
        {
            controlMotor(0, true, false);  
        }
        else if (command == "m1s")
        {
            controlMotor(0, false, true);  
        }
        else
        {
            Serial.println("❌ Invalid command");
        }
    }
}

void stopAllMotors()
{
    isRunning = false;
    digitalWrite(ENABLE_PIN_1, HIGH);
    digitalWrite(STEP_PIN_1, LOW);
    Serial.println("✅ All motors stopped");
}
