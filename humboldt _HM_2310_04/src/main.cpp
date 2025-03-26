#include <Arduino.h>
#include <ADS1X15.h>

ADS1115 ADS1(0x48);  // ที่อยู่ I2C ของเซ็นเซอร์ตัวที่ 1
ADS1115 ADS2(0x49);  // ที่อยู่ I2C ของเซ็นเซอร์ตัวที่ 2

float displacement1 = 0.0;
float displacement2 = 0.0;
float average1 = 0.0;
float average2 = 0.0;
// static float sum1 = 0.0;  
// static float sum2 = 0.0;  
// static int count = 0;    
// static float displacementList1[100] = {0};
// static float displacementList2[100] = {0};

float x_displacement = 0;
float y_displacement = 0;
float counter = 0;

int interval = 1000;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;
int sub_interval = 10;
unsigned long sub_currentMillis = 0;
unsigned long sub_previousMillis = 0;

void setup() 
{
  Serial.begin(115200);
  // Serial.print("System online 🌟 ✅\n");
  Wire.begin();
  ADS1.begin();
  ADS1.setGain(16);
  ADS1.setDataRate(7);
  ADS2.begin();
  ADS2.setGain(16);
  ADS2.setDataRate(7);

  // clear data
  x_displacement = 0;
  y_displacement = 0;
  counter = 0;
  currentMillis = millis();
  previousMillis = millis();
  sub_currentMillis = millis();
  sub_previousMillis = millis();
}

void loop() 
{
  unsigned long sub_currentMillis = millis();
  if (sub_currentMillis - sub_previousMillis >= sub_interval)
  {
    sub_previousMillis = sub_currentMillis;

    int16_t val_01 = ADS1.readADC_Differential_0_1();  
    int16_t val_02 = ADS2.readADC_Differential_0_1();
    float volts_01 = ADS1.toVoltage(val_01); 
    float volts_02 = ADS2.toVoltage(val_02); 

    displacement1 = 100*((volts_01 / 3.65) * 17.00); 
    displacement2 = 100*((volts_02 / 3.65) * 25.00);

    x_displacement += displacement1;
    y_displacement += displacement2;
    counter++;
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
    // find average and print
    x_displacement = x_displacement / counter;
    y_displacement = y_displacement / counter;
    Serial.print(x_displacement, 3);
    Serial.print(", ");
    Serial.println(y_displacement, 3);

    x_displacement = 0;
    y_displacement = 0;
    counter = 0;
  }


    // displacementList1[count] = displacement1;
    // sum1 += displacement1;
    // displacementList2[count] = displacement2;
    // sum2 += displacement2;
    // count++;

    // if (count == 100) {
    //   average1 = sum1 / 100;  
    //   average2 = sum2 / 100;  
    //   Serial.print(average1, 3);
    //   Serial.print(", ");
    //   Serial.println(average2, 3);
    //   sum1 = 0.0;
    //   sum2 = 0.0;
    //   count = 0;
    // }

  }