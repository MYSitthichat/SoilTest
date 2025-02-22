#include <Arduino.h>

#define DIR_PIN 7
#define STEP_PIN 9
#define SWITCH_UP 14
#define SWITCH_DOWN 15

#define ENABLE_PIN 8

bool isRunning = false;
bool BtIsRunning = false;

bool direction = true;
unsigned long lastPulseTime = 0;
unsigned long pulseInterval = 5000; // Default to lowest speed
bool stepState = false;
String serialBuffer = "";

void stopMotorBeforeDirectionChange();
void handleSerialCommand();
void controlMotor(bool state, bool dir);

char button_up_state = 0xFF;
char button_down_state = 0xFF;

unsigned long pulseManualInterval = 1000;
unsigned long lastPulseManualTime = 0;

void setup()
{
    pinMode(DIR_PIN, OUTPUT);
    pinMode(STEP_PIN, OUTPUT);
    pinMode(SWITCH_UP, INPUT_PULLUP);
    pinMode(SWITCH_DOWN, INPUT_PULLUP);
    pinMode(ENABLE_PIN, OUTPUT);
    Serial.begin(115200);
    Serial.println("Setup complete");
}

void loop()
{
    handleSerialCommand();
    if(isRunning == false)
    {
        button_up_state = (button_up_state << 1) + digitalRead(SWITCH_UP);
        button_down_state = (button_down_state << 1) + digitalRead(SWITCH_DOWN);
        if (button_up_state == 0x00)
        {
            BtIsRunning = true;
            direction = true;
            digitalWrite(DIR_PIN, HIGH);
            pulseInterval = 44;
            digitalWrite(ENABLE_PIN, LOW);
        }
        else if (button_down_state == 0x00)
        {
            BtIsRunning = true;
            direction = false;
            pulseInterval = 44;
            digitalWrite(DIR_PIN, LOW);
            digitalWrite(ENABLE_PIN, LOW);
        }
        else
        {
            BtIsRunning = false;
            digitalWrite(ENABLE_PIN, HIGH);
        }
    }
    if (isRunning && (micros() - lastPulseTime >= pulseInterval)) //motor is running
    {
        lastPulseTime = micros();
        stepState = !stepState;
        digitalWrite(STEP_PIN, stepState);
    }
    if (BtIsRunning && (micros() - lastPulseTime >= pulseInterval)) //button is pressed
    {
        lastPulseTime = micros();
        stepState = !stepState;
        digitalWrite(STEP_PIN, stepState);
    }
}
void handleSerialCommand()
{
    if (Serial.available())
    {
        char received = Serial.read();
        if (received == '\n')
        {
            serialBuffer.trim();
            if (serialBuffer == "r,0")
            {
                isRunning = false;
                digitalWrite(STEP_PIN, LOW);
                digitalWrite(ENABLE_PIN, HIGH);
                Serial.println("Motor stopped");
            }
            else if (serialBuffer.startsWith("s,"))
            {
                int rpm = serialBuffer.substring(2).toInt();
                if (rpm >= 0 && rpm <= 1000)
                {
                    pulseInterval = rpm > 0 ? (200000 / (rpm * 9)) : 200000;
                    Serial.print(rpm);
                }
                else
                {
                    Serial.println("Invalid RPM (0-100)");
                }
            }
            else if (serialBuffer == "r,1")
            {
                isRunning = true;
                digitalWrite(ENABLE_PIN, LOW);
            }
            else if (serialBuffer == "d,1")
            {
                if (direction != true)
                {
                    stopMotorBeforeDirectionChange();
                }
                isRunning = true;
                direction = true;
                digitalWrite(DIR_PIN, HIGH);
            }
            else if (serialBuffer == "d,0")
            {
                if (direction != false)
                {
                    stopMotorBeforeDirectionChange();
                }
                isRunning = true;
                direction = false;
                digitalWrite(DIR_PIN, LOW);
            }
            else
            {
                Serial.println("Invalid command");
            }
            serialBuffer = "";
        }
        else
        {
            serialBuffer += received;
        }
    }
}
void stopMotorBeforeDirectionChange()
{
    isRunning = false;
    delay(50);
}