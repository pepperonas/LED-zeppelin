#!/usr/bin/env python3

# 🎵🔥 DEMO MODE - SMOOTH LED ANIMATIONS WITHOUT AUDIO ISSUES! 🔥🎵

import gpiozero
import time
import random
import math
import numpy as np
from beat_detector import BeatDetector
import atexit

# LED Konfiguration
LED_COUNT = 300
BRIGHTNESS = 0.9
LED_PIN = 18

# GPIO cleanup and initialization
def cleanup_gpio():
    try:
        if 'led_output' in globals() and led_output:
            led_output.close()
    except:
        pass
    try:
        gpiozero.Device.pin_factory.reset()
    except:
        pass

# Register cleanup
atexit.register(cleanup_gpio)

# Try to cleanup any existing GPIO usage
cleanup_gpio()

# Initialize GPIO
led_output = None
try:
    led_output = gpiozero.OutputDevice(LED_PIN)
except Exception as e:
    print(f"❌ GPIO Error: {e}")
    print("🔄 Trying alternative GPIO initialization...")
    time.sleep(1)
    try:
        led_output = gpiozero.OutputDevice(LED_PIN)
    except Exception as e2:
        print(f"❌ Still can't access GPIO pin {LED_PIN}: {e2}")
        print("💡 Try running: sudo killall python3 && sudo systemctl restart pigpiod")
        exit(1)

# Import all the LED functions from music_mode
exec(open('/home/pi/led/raspi/music_mode.py').read().split('def main()')[0])

def main():
    global current_mode, shutdown_requested
    
    print("🎵🔥🔥🔥 DEMO MODE AKTIVIERT! 🔥🔥🔥🎵")
    print("300 LEDs - PERFEKT GLATTE ANIMATIONEN - KEINE AUDIO-PROBLEME!")
    print("📊 SIMULIERT 120 BPM MUSIK FÜR TOLLE LED-EFFEKTE!")
    
    print("\nModi:")
    print("  spectrum       - Frequency spectrum analyzer")
    print("  energy_wave    - Energy wave effect") 
    print("  bass_pulse     - Bass-focused pulse")
    print("  reactive_rainbow - Music-reactive rainbow")
    print("  beat_flash     - Flash on every beat")
    print("  strobe         - Beat-synchronized strobe")
    print("\nStrg+C zum Beenden")
    print("Drücke Enter zum Wechseln der Modi\n")
    
    # Initialize beat detector in demo mode only
    detector = BeatDetector(sample_rate=44100, chunk_size=1024)
    detector.add_beat_callback(on_beat)
    detector.add_audio_callback(on_audio_frame)
    
    # Start demo mode directly
    print("🎵 Starte Demo-Modus für perfekte LED-Animationen!")
    print("💡 120 BPM Simulation - garantiert keine Audio-Fehler!")
    
    if not detector.start(demo_mode=True):
        print("❌ Fehler beim Starten des Demo-Modus!")
        return
    
    try:
        print(f"🎛️ Aktueller Modus: {current_mode}")
        print("🎵 Genieße die glatten LED-Animationen!")
        
        # Mode switching thread
        import threading
        import select
        import sys
        
        def mode_switcher():
            global shutdown_requested
            while not shutdown_requested:
                try:
                    # Non-blocking input check
                    if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                        input()  # Consume the input
                        if not shutdown_requested:
                            cycle_mode()
                except:
                    break
                time.sleep(0.1)
        
        # Start mode switching thread
        mode_thread = threading.Thread(target=mode_switcher, daemon=False)
        mode_thread.start()
        
        # Main loop
        while not shutdown_requested:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        shutdown_requested = True
        print("\n🎉 DEMO MODE ENDE! 🎉")
        
        # Proper shutdown sequence
        try:
            detector.stop()
            time.sleep(0.2)  # Allow audio callbacks to finish
            clear()
            cleanup_gpio()
            
            # Wait for mode thread to finish
            if 'mode_thread' in locals() and mode_thread.is_alive():
                mode_thread.join(timeout=1.0)
        except Exception as e:
            print(f"Shutdown error: {e}")
        
        print("✅ Clean shutdown completed")

if __name__ == "__main__":
    main()