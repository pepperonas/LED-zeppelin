#!/usr/bin/env python3

# 🔥🔥🔥 PARTY MODE - GEILE EFFEKTE FÜR 300 LEDs! 🔥🔥🔥

import gpiozero
import time
import random
import math

# LED Konfiguration
LED_COUNT = 300
BRIGHTNESS = 0.9  # VOLLE POWER!
LED_PIN = 18

led_output = gpiozero.OutputDevice(LED_PIN)
leds = [(0, 0, 0)] * LED_COUNT

# Timing optimiert
T1H_NS = 800
T1L_NS = 400
T0H_NS = 400
T0L_NS = 800
RESET_NS = 50000

def precise_delay_ns(nanoseconds):
    if nanoseconds < 10000:
        start = time.perf_counter_ns()
        while (time.perf_counter_ns() - start) < nanoseconds:
            pass
    else:
        time.sleep(nanoseconds / 1_000_000_000)

def send_bit(bit):
    if bit:
        led_output.on()
        precise_delay_ns(T1H_NS)
        led_output.off()
        precise_delay_ns(T1L_NS)
    else:
        led_output.on()
        precise_delay_ns(T0H_NS)
        led_output.off()
        precise_delay_ns(T0L_NS)

def send_byte(byte):
    for bit in range(7, -1, -1):
        send_bit(byte & (1 << bit))

def send_to_strip():
    led_output.off()
    precise_delay_ns(RESET_NS)
    
    for r, g, b in leds:
        r = int(r * BRIGHTNESS)
        g = int(g * BRIGHTNESS)
        b = int(b * BRIGHTNESS)
        send_byte(g)
        send_byte(r)
        send_byte(b)
    
    led_output.off()
    precise_delay_ns(RESET_NS)

def clear():
    global leds
    leds = [(0, 0, 0)] * LED_COUNT
    send_to_strip()

def set_pixel(index, r, g, b):
    if 0 <= index < LED_COUNT:
        leds[index] = (r, g, b)

def hsv_to_rgb(h, s, v):
    """HSV zu RGB - für geile Farben"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

# 🌈 EFFEKT 1: RAINBOW CHASE
def rainbow_chase(speed=0.01):
    """Regenbogen läuft durch den Strip"""
    print("🌈 RAINBOW CHASE!")
    
    for offset in range(360 * 3):  # 3 komplette Zyklen
        for i in range(LED_COUNT):
            hue = (offset + i * 2) % 360
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            set_pixel(i, r, g, b)
        
        send_to_strip()
        time.sleep(speed)

# ⚡ EFFEKT 2: LIGHTNING STORM
def lightning_storm():
    """Heftiges Gewitter mit mehreren Blitzen"""
    print("⚡ LIGHTNING STORM!")
    
    for _ in range(15):  # 15 Blitze
        # Zufällige Blitz-Parameter
        num_strikes = random.randint(1, 4)
        
        for strike in range(num_strikes):
            clear()
            
            # Mehrere Blitz-Bereiche
            for _ in range(random.randint(2, 5)):
                start = random.randint(0, LED_COUNT - 80)
                length = random.randint(30, 80)
                intensity = random.randint(150, 255)
                
                for i in range(start, min(start + length, LED_COUNT)):
                    set_pixel(i, intensity, intensity, intensity)
            
            send_to_strip()
            time.sleep(random.uniform(0.01, 0.05))
            
            clear()
            time.sleep(random.uniform(0.02, 0.08))
        
        # Pause zwischen Gewittern
        time.sleep(random.uniform(0.3, 1.0))

# 🔥 EFFEKT 3: FIRE SIMULATION
def fire_simulation():
    """Realistisches Feuer"""
    print("🔥 FIRE SIMULATION!")
    
    heat = [0] * LED_COUNT
    
    for _ in range(500):  # 50 Sekunden Feuer
        # Kühle alle Pixel ab
        for i in range(LED_COUNT):
            heat[i] = max(0, heat[i] - random.randint(0, 3))
        
        # Heiße Spots am Ende (Feuer-Basis)
        for i in range(LED_COUNT - 10, LED_COUNT):
            if random.random() < 0.7:
                heat[i] = min(255, heat[i] + random.randint(50, 100))
        
        # Hitze nach oben verteilen
        for i in range(LED_COUNT - 1, 2, -1):
            heat[i] = (heat[i - 1] + heat[i - 2] + heat[i - 2]) // 3
        
        # Hitze zu Farbe konvertieren
        for i in range(LED_COUNT):
            h = heat[i]
            if h < 85:
                # Schwarz zu Rot
                r = h * 3
                g = 0
                b = 0
            elif h < 170:
                # Rot zu Gelb
                r = 255
                g = (h - 85) * 3
                b = 0
            else:
                # Gelb zu Weiß
                r = 255
                g = 255
                b = (h - 170) * 3
            
            set_pixel(i, r, g, b)
        
        send_to_strip()
        time.sleep(0.05)

# 💥 EFFEKT 4: MATRIX RAIN
def matrix_rain():
    """Matrix-Regen Effekt"""
    print("💥 MATRIX RAIN!")
    
    drops = []
    
    for _ in range(1000):  # Lange Matrix-Session
        # Neue Tropfen
        if random.random() < 0.3:
            drops.append({
                'pos': 0,
                'speed': random.uniform(0.5, 2.0),
                'length': random.randint(10, 30),
                'color': random.choice([(0, 255, 0), (0, 255, 100), (50, 255, 50)])
            })
        
        # Alle LEDs dimmen
        for i in range(LED_COUNT):
            r, g, b = leds[i]
            leds[i] = (max(0, r - 10), max(0, g - 5), max(0, b - 10))
        
        # Tropfen bewegen und zeichnen
        for drop in drops[:]:
            drop['pos'] += drop['speed']
            
            # Tropfen zeichnen
            for i in range(int(drop['length'])):
                pos = int(drop['pos']) - i
                if 0 <= pos < LED_COUNT:
                    intensity = max(0, 255 - i * 15)
                    r = (drop['color'][0] * intensity) // 255
                    g = (drop['color'][1] * intensity) // 255
                    b = (drop['color'][2] * intensity) // 255
                    set_pixel(pos, r, g, b)
            
            # Tropfen entfernen wenn unten
            if drop['pos'] > LED_COUNT + drop['length']:
                drops.remove(drop)
        
        send_to_strip()
        time.sleep(0.03)

# 🌊 EFFEKT 5: WAVE INTERFERENCE
def wave_interference():
    """Zwei interferierende Wellen"""
    print("🌊 WAVE INTERFERENCE!")
    
    for frame in range(600):  # 60 Sekunden
        for i in range(LED_COUNT):
            # Zwei Sinus-Wellen
            wave1 = math.sin((i * 0.1) + (frame * 0.1)) * 127 + 128
            wave2 = math.sin((i * 0.05) + (frame * 0.15)) * 127 + 128
            
            # Interferenz
            interference = (wave1 + wave2) / 2
            
            # Zu Farbe konvertieren
            hue = (interference + frame) % 360
            r, g, b = hsv_to_rgb(hue, 1.0, interference / 255)
            
            set_pixel(i, r, g, b)
        
        send_to_strip()
        time.sleep(0.05)

# 🎆 EFFEKT 6: FIREWORKS
def fireworks():
    """Feuerwerk-Show"""
    print("🎆 FIREWORKS SHOW!")
    
    for _ in range(20):  # 20 Feuerwerke
        # Rakete steigt auf
        launch_pos = random.randint(50, LED_COUNT - 50)
        
        for i in range(40):
            clear()
            # Raketen-Trail
            for j in range(5):
                pos = launch_pos - i - j
                if pos >= 0:
                    intensity = 255 - j * 50
                    set_pixel(pos, intensity, intensity // 2, 0)
            
            send_to_strip()
            time.sleep(0.02)
        
        # Explosion
        explosion_pos = launch_pos - 40
        explosion_color = hsv_to_rgb(random.randint(0, 360), 1.0, 1.0)
        
        for radius in range(50):
            # Explosion ausbreiten
            for i in range(-radius, radius + 1):
                pos = explosion_pos + i
                if 0 <= pos < LED_COUNT:
                    distance = abs(i)
                    if distance <= radius:
                        intensity = max(0, 255 - distance * 8)
                        r = (explosion_color[0] * intensity) // 255
                        g = (explosion_color[1] * intensity) // 255
                        b = (explosion_color[2] * intensity) // 255
                        set_pixel(pos, r, g, b)
            
            # Funken
            for _ in range(random.randint(3, 8)):
                spark_pos = explosion_pos + random.randint(-radius - 10, radius + 10)
                if 0 <= spark_pos < LED_COUNT:
                    set_pixel(spark_pos, 255, 255, 255)
            
            send_to_strip()
            time.sleep(0.03)
            
            # Dimmen
            for i in range(LED_COUNT):
                r, g, b = leds[i]
                leds[i] = (max(0, r - 8), max(0, g - 8), max(0, b - 8))
        
        time.sleep(random.uniform(0.5, 2.0))

def main():
    print("🎉🎉🎉 PARTY MODE AKTIVIERT! 🎉🎉🎉")
    print("5 METER - 300 LEDs - VOLLE POWER!")
    print("Strg+C zum Beenden\n")
    
    effects = [
        ("🌈 RAINBOW CHASE", rainbow_chase),
        ("⚡ LIGHTNING STORM", lightning_storm),
        ("🔥 FIRE SIMULATION", fire_simulation),
        ("💥 MATRIX RAIN", matrix_rain),
        ("🌊 WAVE INTERFERENCE", wave_interference),
        ("🎆 FIREWORKS SHOW", fireworks)
    ]
    
    try:
        while True:
            for name, effect in effects:
                print(f"\n{name}")
                effect()
                clear()
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🎉 PARTY ENDE! 🎉")
        clear()

if __name__ == "__main__":
    main()