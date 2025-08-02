#!/usr/bin/env python3

# 🎵🔥 MUSIC MODE - BEAT-REACTIVE LED STRIP! 🔥🎵

import gpiozero
import time
import random
import math
import numpy as np
from beat_detector import BeatDetector
import atexit

# LED Konfiguration (gleich wie party_mode.py)
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
leds = [(0, 0, 0)] * LED_COUNT
previous_leds = [(0, 0, 0)] * LED_COUNT  # For smooth transitions

# Timing für WS2812B (gleich wie party_mode.py)
T1H_NS = 800
T1L_NS = 400
T0H_NS = 400
T0L_NS = 800
RESET_NS = 50000

# Music visualization state
current_mode = "spectrum"
beat_intensity = 0
bass_level = 0
energy_history = []
beat_flash_time = 0
led_update_rate = 30  # Target FPS for smooth animations
last_led_update = 0
shutdown_requested = False

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
    global shutdown_requested, previous_leds
    if shutdown_requested or not led_output:
        return
    
    try:
        # Store current state for next smoothing
        previous_leds = leds.copy()
        
        led_output.off()
        precise_delay_ns(RESET_NS)
        
        for r, g, b in leds:
            if shutdown_requested:
                return
            r = int(r * BRIGHTNESS)
            g = int(g * BRIGHTNESS)
            b = int(b * BRIGHTNESS)
            send_byte(g)
            send_byte(r)
            send_byte(b)
        
        led_output.off()
        precise_delay_ns(RESET_NS)
    except Exception as e:
        if not shutdown_requested:
            print(f"Strip send error: {e}")

def clear():
    global leds
    leds = [(0, 0, 0)] * LED_COUNT
    send_to_strip()

def set_pixel(index, r, g, b, smooth_factor=0.7):
    """Set pixel with optional smoothing"""
    if 0 <= index < LED_COUNT:
        # Apply smoothing by blending with previous value
        if smooth_factor < 1.0:
            old_r, old_g, old_b = previous_leds[index]
            r = int(old_r * (1 - smooth_factor) + r * smooth_factor)
            g = int(old_g * (1 - smooth_factor) + g * smooth_factor)
            b = int(old_b * (1 - smooth_factor) + b * smooth_factor)
        
        leds[index] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

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

# 🎵 MUSIC REACTIVE EFFECTS

def spectrum_analyzer(freq_bands, volume):
    """Frequency spectrum analyzer visualization with smooth transitions"""
    # Don't clear - let smoothing handle the fade
    
    # Map frequency bands to LED sections
    band_size = LED_COUNT // 4
    
    # Clear all pixels with fade
    for i in range(LED_COUNT):
        set_pixel(i, 0, 0, 0, smooth_factor=0.3)  # Slower fade out
    
    for band_idx, energy in enumerate(freq_bands):
        start_led = band_idx * band_size
        end_led = min((band_idx + 1) * band_size, LED_COUNT)
        
        # Scale energy to LED height with better sensitivity
        energy_scaled = min(1.0, energy * 30)  # Reduced sensitivity for smoother motion
        leds_to_light = int(energy_scaled * band_size)
        
        # Enhanced colors for each band
        colors = [
            (255, 50, 50),   # Bass - Bright Red
            (255, 150, 0),   # Low-mid - Orange
            (50, 255, 50),   # High-mid - Bright Green
            (100, 100, 255)  # Treble - Bright Blue
        ]
        
        # Light up LEDs for this band with smooth transitions
        for i in range(band_size):
            led_pos = start_led + i
            
            if i < leds_to_light:
                # Intensity decreases from bottom to top
                intensity = 1.0 - (i / band_size) * 0.7  # Less dramatic fade
                r, g, b = colors[band_idx]
                set_pixel(led_pos, int(r * intensity), int(g * intensity), int(b * intensity), smooth_factor=0.6)
            else:
                # Fade out unused LEDs
                set_pixel(led_pos, 0, 0, 0, smooth_factor=0.2)

def beat_flash(energy, volume, freq_bands):
    """Flash effect on beat detection"""
    global beat_flash_time, beat_intensity
    
    beat_flash_time = time.time()
    beat_intensity = min(1.0, energy * 20)  # Scale beat intensity
    
    # Random flash color based on dominant frequency
    max_band = np.argmax(freq_bands)
    flash_colors = [
        (255, 0, 0),    # Bass - Red
        (255, 255, 0),  # Low-mid - Yellow
        (0, 255, 255),  # High-mid - Cyan
        (255, 0, 255)   # Treble - Magenta
    ]
    
    # Flash entire strip with beat color
    flash_color = flash_colors[max_band]
    flash_brightness = beat_intensity
    
    for i in range(LED_COUNT):
        r, g, b = flash_color
        set_pixel(i, int(r * flash_brightness), int(g * flash_brightness), int(b * flash_brightness))

def energy_wave(freq_bands, volume):
    """Moving wave based on energy levels with smooth motion"""
    global energy_history
    
    # Add current energy to history
    total_energy = sum(freq_bands)
    energy_history.append(total_energy)
    if len(energy_history) > LED_COUNT:
        energy_history.pop(0)
    
    # Clear with fade
    for i in range(LED_COUNT):
        set_pixel(i, 0, 0, 0, smooth_factor=0.1)
    
    # Create wave effect with smoother motion
    for i in range(min(len(energy_history), LED_COUNT)):
        energy_val = energy_history[i] if i < len(energy_history) else 0
        
        # Scale energy to color intensity
        intensity = min(1.0, energy_val * 80)  # Adjusted sensitivity
        
        # Create color based on position and energy with slower movement
        hue = (i * 3 + time.time() * 30) % 360  # Slower color cycling
        r, g, b = hsv_to_rgb(hue, 0.9, intensity)
        
        set_pixel(LED_COUNT - 1 - i, r, g, b, smooth_factor=0.7)

def bass_pulse(freq_bands, volume):
    """Pulse effect focused on bass frequencies"""
    global bass_level
    
    # Get bass energy (first frequency band)
    bass_energy = freq_bands[0] if freq_bands else 0
    bass_level = bass_energy * 50  # Scale sensitivity
    
    # Create expanding circle from center
    center = LED_COUNT // 2
    max_radius = min(center, int(bass_level * center))
    
    for i in range(LED_COUNT):
        distance_from_center = abs(i - center)
        
        if distance_from_center <= max_radius:
            # Intensity decreases with distance
            intensity = 1.0 - (distance_from_center / max_radius)
            
            # Color based on bass intensity
            r = int(255 * intensity)
            g = int(50 * intensity)
            b = int(150 * intensity)
            
            set_pixel(i, r, g, b)
        else:
            set_pixel(i, 0, 0, 0)

def reactive_rainbow(freq_bands, volume):
    """Rainbow effect that reacts to music with smooth motion"""
    # Rainbow speed based on volume but more controlled
    speed = 50 + (volume * 100)  # Base speed + volume boost
    
    for i in range(LED_COUNT):
        # Hue based on position and time, speed influenced by volume
        hue = (i * 2 + time.time() * speed) % 360
        
        # Saturation and brightness based on frequency bands
        total_energy = sum(freq_bands) if freq_bands else 0
        brightness = 0.4 + (total_energy * 15)  # Minimum brightness + energy boost
        brightness = min(1.0, brightness)
        
        r, g, b = hsv_to_rgb(hue, 0.9, brightness)
        set_pixel(i, r, g, b, smooth_factor=0.8)  # Very smooth transitions

def strobe_beat(freq_bands, volume):
    """Strobe effect synchronized with beats"""
    # Only light up on recent beat
    current_time = time.time()
    if current_time - beat_flash_time < 0.1:  # 100ms strobe duration
        # White strobe with intensity based on beat
        intensity = int(255 * beat_intensity)
        for i in range(LED_COUNT):
            set_pixel(i, intensity, intensity, intensity)
    else:
        clear()

# Audio callback functions
def on_beat(energy, volume, freq_bands):
    """Called when beat is detected"""
    global current_mode
    
    print(f"🥁 BEAT! Mode: {current_mode}, Energy: {energy:.3f}")
    
    if current_mode == "beat_flash":
        beat_flash(energy, volume, freq_bands)
    elif current_mode == "strobe":
        beat_flash(energy, volume, freq_bands)

def on_audio_frame(energy, volume, freq_bands, beat_detected):
    """Called for every audio frame with frame rate limiting"""
    global current_mode, last_led_update, shutdown_requested
    
    if shutdown_requested:
        return
    
    current_time = time.time()
    
    # Frame rate limiting for smoother LED updates
    if current_time - last_led_update < (1.0 / led_update_rate):
        return
    
    last_led_update = current_time
    
    # Live volume display (update every ~100ms for more responsive feedback)
    if hasattr(on_audio_frame, 'last_display_time'):
        if current_time - on_audio_frame.last_display_time > 0.1:
            display_live_audio(energy, volume, freq_bands, beat_detected)
            on_audio_frame.last_display_time = current_time
    else:
        on_audio_frame.last_display_time = current_time
    
    try:
        if current_mode == "spectrum":
            spectrum_analyzer(freq_bands, volume)
        elif current_mode == "energy_wave":
            energy_wave(freq_bands, volume)
        elif current_mode == "bass_pulse":
            bass_pulse(freq_bands, volume)
        elif current_mode == "reactive_rainbow":
            reactive_rainbow(freq_bands, volume)
        elif current_mode == "strobe" and not beat_detected:
            # Keep strobe dark between beats
            strobe_beat(freq_bands, volume)
        
        # Update LEDs safely
        if led_output and not shutdown_requested:
            send_to_strip()
    except Exception as e:
        if not shutdown_requested:
            print(f"LED update error: {e}")

def display_live_audio(energy, volume, freq_bands, beat_detected):
    """Display enhanced live audio levels with improved visualization"""
    # Volume bar (30 characters) - larger for better visibility
    volume_bar_length = 30
    volume_level = min(volume_bar_length, int(volume * volume_bar_length * 20))
    volume_bar = "█" * volume_level + "░" * (volume_bar_length - volume_level)
    
    # Energy bar (25 characters) - larger and more sensitive
    energy_bar_length = 25
    energy_level = min(energy_bar_length, int(energy * energy_bar_length * 5))
    energy_bar = "▓" * energy_level + "░" * (energy_bar_length - energy_level)
    
    # Enhanced frequency bands bars (15 characters each)
    band_names = ["🔊Bass", "🎸LMid", "🎹HMid", "✨Treb"]
    band_bars = []
    for i, band_energy in enumerate(freq_bands):
        band_level = min(15, int(band_energy * 15 * 40))
        # Use different characters for different intensity levels
        if band_level > 10:
            band_bar = "█" * band_level + "░" * (15 - band_level)
        elif band_level > 5:
            band_bar = "▓" * band_level + "░" * (15 - band_level)
        else:
            band_bar = "▒" * band_level + "░" * (15 - band_level)
        band_bars.append(f"{band_names[i]}:{band_bar}")
    
    # Enhanced beat indicator with volume-based sizing
    if beat_detected:
        if volume > 0.7:
            beat_symbol = "💥🥁💥"
        elif volume > 0.4:
            beat_symbol = "🔥🥁🔥"
        else:
            beat_symbol = "⚡🥁⚡"
    else:
        beat_symbol = "   "
    
    # Volume level indicator with numeric values
    if volume > 0.8:
        vol_indicator = f"🔊LOUD ({volume:.2f})"
    elif volume > 0.5:
        vol_indicator = f"🔉MED  ({volume:.2f})"
    elif volume > 0.2:
        vol_indicator = f"🔈LOW  ({volume:.2f})"
    else:
        vol_indicator = f"🔇QUIET({volume:.2f})"
    
    # Peak volume indicator (running max)
    if not hasattr(display_live_audio, 'peak_volume'):
        display_live_audio.peak_volume = 0
    if volume > display_live_audio.peak_volume:
        display_live_audio.peak_volume = volume
    # Slowly decay peak
    display_live_audio.peak_volume *= 0.995
    
    # Clear previous lines and print enhanced live data
    print(f"\r\033[K{beat_symbol} {vol_indicator} Peak:{display_live_audio.peak_volume:.2f}", flush=True)
    print(f"\033[K📊 Vol:{volume_bar} Energy:{energy_bar}", flush=True)
    print(f"\033[K🎵 {' '.join(band_bars)}", flush=True)
    # Move cursor back up to overwrite on next update
    print("\033[3A", end="", flush=True)

def cycle_mode():
    """Cycle through different visualization modes"""
    global current_mode
    
    modes = ["spectrum", "energy_wave", "bass_pulse", "reactive_rainbow", "beat_flash", "strobe"]
    current_index = modes.index(current_mode)
    current_mode = modes[(current_index + 1) % len(modes)]
    
    print(f"🎛️ Switched to mode: {current_mode}")

def main():
    global current_mode, shutdown_requested
    
    print("🎵🔥🔥🔥 MUSIC MODE AKTIVIERT! 🔥🔥🔥🎵")
    print("300 LEDs - BEAT-REACTIVE - GEILE MUSIK-VISUALISIERUNG!")
    print("📊 LIVE VOLUME VISUALISIERUNG AKTIVIERT! 📊")
    print("\nModi:")
    print("  spectrum       - Frequency spectrum analyzer")
    print("  energy_wave    - Energy wave effect") 
    print("  bass_pulse     - Bass-focused pulse")
    print("  reactive_rainbow - Music-reactive rainbow")
    print("  beat_flash     - Flash on every beat")
    print("  strobe         - Beat-synchronized strobe")
    print("\n📊 Live Audio Display:")
    print("  🔊 Volume bars, energy levels & frequency bands")
    print("  🥁 Beat detection with visual indicators")
    print("  🎵 Real-time audio analysis")
    print("\nStrg+C zum Beenden")
    print("Drücke Enter zum Wechseln der Modi\n")
    
    # Initialize beat detector
    detector = BeatDetector(sample_rate=44100, chunk_size=1024)
    detector.add_beat_callback(on_beat)
    detector.add_audio_callback(on_audio_frame)
    
    # Start audio detection - try real audio first, fallback to demo mode
    if not detector.start():
        print("❌ Mikrofon nicht verfügbar - starte DEMO MODUS!")
        print("🎵 Simuliert Musik mit 120 BPM für LED-Test")
        print("💡 Demo Modus ist perfekt zum Testen der LED-Effekte!")
        if not detector.start(demo_mode=True):
            print("❌ Fehler beim Starten des Audio-Detektors!")
            return
    
    try:
        print(f"🎛️ Aktueller Modus: {current_mode}")
        print("🎵 Spiele Musik ab und schau den LEDs zu!")
        
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
        print("\n🎉 MUSIC MODE ENDE! 🎉")
        
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