#include <JeeLib.h>
#include <LocLib.h>

// jeenode ports where ledstate is plugged
LedStatePlug ledstate(2, 3);
MilliTimer timer;
int blinkPeriod = 1000;
int delta = 500;
bool state = true;

void setup () {
  Serial.begin(57600);
  Serial.println("\n[led_f]");

  ledstate.set(2);
}

void loop () {
  byte event = ledstate.buttonCheck();

  switch (event) {

  case BlinkPlug::OFF1:
    blinkPeriod += delta;
    Serial.println("  Button 1 released");
    break;

  case BlinkPlug::OFF2:
    if (blinkPeriod > delta)
      blinkPeriod -= delta;
    Serial.println("  Button 2 released");
    break;
  }

    // report these other events only once a second
    if (timer.poll(blinkPeriod)) {
      if (state){
        ledstate.set(0);
        state = false;
      }
      else
      {
        ledstate.set(2);
        state = true;
    }
  }
}
