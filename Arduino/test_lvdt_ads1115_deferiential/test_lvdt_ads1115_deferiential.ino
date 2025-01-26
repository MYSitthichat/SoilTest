#include <Wire.h>
#include <Adafruit_ADS1X15.h>

// สร้างออบเจ็กต์สำหรับ ADS1115
Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(115200);
  
  // เริ่มต้นโมดูล ADS1115
  if (!ads.begin()) {
    Serial.println("ไม่สามารถเชื่อมต่อกับ ADS1115 ได้");
    while (1);
  }
  Serial.println("เริ่มต้น ADS1115 สำเร็จ");

  // ตั้งค่า PGA (ตัวขยายสัญญาณ) เป็น ±4.096V
  ads.setGain(GAIN_ONE); // ตัวเลือก: GAIN_TWOTHIRDS, GAIN_ONE, GAIN_TWO, GAIN_FOUR, GAIN_EIGHT, GAIN_SIXTEEN
}

void loop() {
  // อ่านค่า Differential ระหว่าง A0 และ A1
  int16_t adcValue = ads.readADC_Differential_0_1();

  // แปลงค่า ADC เป็นแรงดันไฟ (mV)
  float voltage = (adcValue * 0.125)*100; // ตัวคูณนี้ขึ้นอยู่กับการตั้งค่า PGA

  // แสดงผลใน Serial Monitor
  Serial.print("Differential Voltage (A0-A1): ");
  Serial.print(voltage);
  Serial.println(" mV");

  delay(1000); // หน่วงเวลา 1 วินาที
}
