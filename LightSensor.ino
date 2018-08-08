#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);
// The above is necessary to use the tsl module

unsigned long currentMillis; // variables to monitor the time passed when the Sensor is used
unsigned long startMillis;
unsigned long endMillis;

void setup() {
  Serial.begin(9600); // Must have for using serial communication with computer
  tsl.setGain(TSL2591_GAIN_MED); // Sets the base gain value as medium
  startMillis = millis(); // Begins monitoring time passing 
}

void loop() {
  currentMillis = millis(); // How much time has currently passed
  endMillis = currentMillis - startMillis; // How much time has passed since the sensor was first used.
  
  uint16_t full = tsl.getLuminosity(TSL2591_FULLSPECTRUM); // stores the raw integer luminosity into two variables
  uint16_t ir = tsl.getLuminosity(TSL2591_INFRARED);   // visible is full - ir

  // Below is used to automate the gain based on certain threshold values
  if (full > 34000) {
    if (tsl.getGain() == TSL2591_GAIN_MAX) {
      tsl.setGain(TSL2591_GAIN_HIGH);
    }
    else if (tsl.getGain() == TSL2591_GAIN_HIGH) {
     tsl.setGain(TSL2591_GAIN_MED);
    }
    else if (tsl.getGain() == TSL2591_GAIN_MED) {
     tsl.setGain(TSL2591_GAIN_LOW);
    }
  }
  if (full < 1300) {
    if (tsl.getGain() == TSL2591_GAIN_LOW) {
      tsl.setGain(TSL2591_GAIN_MED);
    }
    else if (tsl.getGain() == TSL2591_GAIN_MED) {
      tsl.setGain(TSL2591_GAIN_HIGH);
    }
    else if (tsl.getGain() == TSL2591_GAIN_HIGH) {
      tsl.setGain(TSL2591_GAIN_MAX);
    }
  }
  
  uint16_t gain = tsl.getGain(); // Retrieves the gain value as an integer and stores into a variable

  // Below is what is sent through serial communication to the computer
  Serial.print(full);
  Serial.print(" ");
  Serial.print(ir);
  Serial.print(" ");
  Serial.print(endMillis);
  Serial.print(" ");
  Serial.println(gain);

  delay(100);

}
