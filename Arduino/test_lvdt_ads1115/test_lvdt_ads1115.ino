#include <Wire.h>
#include <Adafruit_ADS1X15.h> 
Adafruit_ADS1115 ads1115;
void setup(void)
{
  Serial.begin(9600);
  Serial.println("Hello!");
  Serial.println("Getting single-ended readings from AIN0..3");
  Serial.println("ADC Range: +/- 6.144V (1 bit =  188uV)");
  // 2/3x gain +/- 6.144V  1 bit = 3mV    0.1875mV (default)
  ads1115.begin();
}
void loop(void)
{
  int16_t adc0, adc1, adc2, adc3;
  float volt0, volt1, volt2, volt3;
  adc0 = ads1115.readADC_SingleEnded(0);
  adc1 = ads1115.readADC_SingleEnded(1);
  adc2 = ads1115.readADC_SingleEnded(2);
  adc3 = ads1115.readADC_SingleEnded(3);
  //Convert Back
  volt0 = adc0*0.000188;
  volt1 = adc1*0.000188;
  volt2 = adc2*0.000188;
  volt3 = adc3*0.000188;
  //Print
  Serial.print("AIN0: ");
  Serial.print(adc0);
  Serial.print(" ");
  Serial.print(volt0, 4);
  Serial.println(" vdc");
  Serial.print("AIN1: ");
  Serial.print(adc1);
  Serial.print(" ");
  Serial.print(volt1, 4);
  Serial.println(" vdc");
  Serial.print("AIN2: ");
  Serial.print(adc2);
  Serial.print(" ");
  Serial.print(volt2, 4);
  Serial.println(" vdc");
  Serial.print("AIN3: ");
  Serial.print(adc3);
  Serial.print(" ");
  Serial.print(volt3, 4);
  Serial.println(" vdc");
  Serial.println(" ");
  delay(1000);
}