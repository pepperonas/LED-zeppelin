#include <FastLED.h>

// Konfiguration
#define LED_PIN     6       // Der Datenpin, den du benutzt
#define NUM_LEDS    300     // 5m Strip mit 60 LEDs/m = 300 LEDs
#define BRIGHTNESS  255     // Maximale Helligkeit für mehr Impact
#define LED_TYPE    WS2812B 
#define COLOR_ORDER GRB     

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();
}

// Blitz-Effekt
void lightning() {
  // Zufällige Position für Blitz
  int flashPos = random(NUM_LEDS - 20);
  int flashLength = random(10, 30);
  
  // Vorblitz
  for(int i = 0; i < flashLength; i++) {
    leds[flashPos + i] = CRGB(200, 200, 255);
  }
  FastLED.show();
  delay(20);
  FastLED.clear();
  FastLED.show();
  delay(50);
  
  // Hauptblitz
  for(int i = 0; i < flashLength; i++) {
    leds[flashPos + i] = CRGB::White;
  }
  FastLED.show();
  delay(30);
  
  // Ausblenden
  for(int fade = 255; fade > 0; fade -= 15) {
    for(int i = 0; i < flashLength; i++) {
      leds[flashPos + i].fadeToBlackBy(15);
    }
    FastLED.show();
    delay(5);
  }
  
  FastLED.clear();
  delay(random(100, 500));
}

// Meteor-Effekt
void meteor(CRGB color, int meteorSize, int meteorTrailDecay, boolean meteorRandomDecay) {
  FastLED.clear();
  
  for(int i = 0; i < NUM_LEDS + NUM_LEDS; i++) {
    // Meteor-Schweif ausblenden
    for(int j = 0; j < NUM_LEDS; j++) {
      if((!meteorRandomDecay) || (random(10) > 5)) {
        leds[j].fadeToBlackBy(meteorTrailDecay);
      }
    }
    
    // Meteor zeichnen
    for(int j = 0; j < meteorSize; j++) {
      if((i - j < NUM_LEDS) && (i - j >= 0)) {
        leds[i - j] = color;
      }
    }
    
    FastLED.show();
    delay(10);
  }
}

// Stroboskop-Effekt
void strobe(CRGB color, int strobeCount, int flashDelay, int endPause) {
  for(int j = 0; j < strobeCount; j++) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
    delay(flashDelay);
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();
    delay(flashDelay);
  }
  delay(endPause);
}

// Feuerwerk-Explosion
void firework() {
  // Aufstieg
  int startPos = random(50, NUM_LEDS - 50);
  for(int i = 0; i < 30; i++) {
    FastLED.clear();
    leds[startPos + i] = CRGB::Orange;
    if(i > 0) leds[startPos + i - 1] = CRGB(100, 50, 0);
    if(i > 1) leds[startPos + i - 2] = CRGB(50, 25, 0);
    FastLED.show();
    delay(20);
  }
  
  // Explosion
  int explosionPos = startPos + 30;
  CRGB explosionColor = CHSV(random(256), 255, 255);
  
  for(int radius = 0; radius < 40; radius++) {
    fadeToBlackBy(leds, NUM_LEDS, 50);
    
    // Funken nach links
    if(explosionPos - radius >= 0) {
      leds[explosionPos - radius] = explosionColor;
    }
    // Funken nach rechts
    if(explosionPos + radius < NUM_LEDS) {
      leds[explosionPos + radius] = explosionColor;
    }
    
    // Zufällige Funken
    for(int spark = 0; spark < 5; spark++) {
      int sparkPos = explosionPos + random(-radius, radius);
      if(sparkPos >= 0 && sparkPos < NUM_LEDS) {
        leds[sparkPos] = CRGB::White;
      }
    }
    
    FastLED.show();
    delay(30);
  }
  
  // Ausblenden
  for(int fade = 0; fade < 20; fade++) {
    fadeToBlackBy(leds, NUM_LEDS, 20);
    FastLED.show();
    delay(30);
  }
}

// Konfetti-Effekt
void confetti() {
  fadeToBlackBy(leds, NUM_LEDS, 10);
  int pos = random(NUM_LEDS);
  leds[pos] += CHSV(random(256), 200, 255);
  FastLED.show();
  delay(10);
}

// Regenbogen-Glitzer
void rainbowGlitter() {
  static uint8_t hue = 0;
  
  // Regenbogen-Basis
  fill_rainbow(leds, NUM_LEDS, hue, 7);
  
  // Glitzer hinzufügen
  if(random(100) < 80) {
    for(int i = 0; i < 10; i++) {
      leds[random(NUM_LEDS)] += CRGB::White;
    }
  }
  
  FastLED.show();
  hue++;
  delay(10);
}

// Schneller Farbwechsel
void rapidColorChange() {
  CRGB colors[] = {CRGB::Red, CRGB::Blue, CRGB::Green, CRGB::Yellow, 
                   CRGB::Purple, CRGB::Cyan, CRGB::White, CRGB::Orange};
  
  for(int c = 0; c < 8; c++) {
    fill_solid(leds, NUM_LEDS, colors[c]);
    FastLED.show();
    delay(50);
  }
}

// Polizei-Lichter
void police() {
  // Links rot
  for(int i = 0; i < NUM_LEDS/2; i++) {
    leds[i] = CRGB::Red;
  }
  // Rechts aus
  for(int i = NUM_LEDS/2; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Black;
  }
  FastLED.show();
  delay(100);
  
  // Links aus
  for(int i = 0; i < NUM_LEDS/2; i++) {
    leds[i] = CRGB::Black;
  }
  // Rechts blau
  for(int i = NUM_LEDS/2; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Blue;
  }
  FastLED.show();
  delay(100);
}

// Energie-Welle
void energyWave() {
  static uint8_t energy = 0;
  
  for(int i = 0; i < NUM_LEDS; i++) {
    uint8_t brightness = sin8((energy * 2) + (i * 10));
    uint8_t hue = (energy + (i * 2)) % 256;
    leds[i] = CHSV(hue, 255, brightness);
  }
  
  FastLED.show();
  energy += 3;
  delay(10);
}

void loop() {
  // Blitz-Gewitter
  for(int i = 0; i < 10; i++) {
    lightning();
  }
  
  // Stroboskop in verschiedenen Farben
  strobe(CRGB::White, 10, 50, 100);
  strobe(CRGB::Red, 10, 50, 100);
  strobe(CRGB::Blue, 10, 50, 100);
  
  // Meteore
  meteor(CRGB::White, 10, 64, true);
  meteor(CRGB::Red, 10, 64, true);
  meteor(CRGB::Blue, 10, 64, true);
  
  // Feuerwerk
  for(int i = 0; i < 5; i++) {
    firework();
  }
  
  // Konfetti-Party
  for(int i = 0; i < 300; i++) {
    confetti();
  }
  
  // Regenbogen-Glitzer
  for(int i = 0; i < 300; i++) {
    rainbowGlitter();
  }
  
  // Schnelle Farbwechsel
  for(int i = 0; i < 5; i++) {
    rapidColorChange();
  }
  
  // Polizei-Lichter
  for(int i = 0; i < 50; i++) {
    police();
  }
  
  // Energie-Wellen
  for(int i = 0; i < 500; i++) {
    energyWave();
  }
}