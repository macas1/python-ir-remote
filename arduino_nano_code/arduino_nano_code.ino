#include <IRremote.hpp>
int dataPin = 2;

void setup() {
    Serial.begin(9600);
    while (!Serial); // Wait for Serial
    IrReceiver.begin(dataPin, ENABLE_LED_FEEDBACK);
}

void loop() {
    if (IrReceiver.decode()) {
      Serial.println(IrReceiver.decodedIRData.decodedRawData);
      IrReceiver.resume();
    }
}