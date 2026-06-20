const int EMG_PIN = 32;

unsigned long lastSample = 0;

void setup() {

  Serial.begin(230400);

}

void loop() {

  if (micros() - lastSample >= 833) {

    lastSample += 833;

    int muestra = analogRead(EMG_PIN);

    Serial.println(muestra);
  }

}
