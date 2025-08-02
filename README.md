# LED Zeppelin 🎸⚡

**Epic WS2812B LED Strip Controller for Arduino & Raspberry Pi**

Control 300 LEDs (5m strip) with awesome effects like lightning, meteors, fireworks, and more!

## 🎯 Features

- **300 LEDs Support** - Full 5-meter WS2812B strip control
- **Lightning Storm** - Realistic lightning effects with multiple strikes
- **Meteor Shower** - Shooting meteors with trailing effects  
- **Fireworks Show** - Rockets with colorful explosions
- **Rainbow Chase** - Smooth rainbow animations
- **Fire Simulation** - Realistic fire with heat distribution
- **Matrix Rain** - Matrix-style falling code
- **Wave Interference** - Mathematical wave patterns
- **Police Lights** - Red/blue flashing patterns
- **Strobe Effects** - High-intensity strobing

## 🛠️ Hardware Requirements

### Common
- **WS2812B LED Strip** (5V, 60 LEDs/m, 5m = 300 LEDs)
- **5V Power Supply** (minimum 15A for full brightness)
- **Data Wire** (connect to controller)

### Arduino Version
- **Arduino Uno/Nano/Pro Mini**
- **Data Pin:** Digital Pin 6
- **FastLED Library**

### Raspberry Pi Version  
- **Raspberry Pi 5** (tested)
- **Data Pin:** GPIO18 (Pin 12)
- **gpiozero Library**

## 🔌 Wiring

### Arduino
```
Arduino Pin 6    →  LED Strip DIN
Arduino 5V       →  LED Strip 5V (or external PSU)
Arduino GND      →  LED Strip GND + PSU GND
```

### Raspberry Pi 5
```
GPIO18 (Pin 12)  →  LED Strip DIN  
Pi 5V (Pin 2)    →  LED Strip 5V (or external PSU)
Pi GND (Pin 6)   →  LED Strip GND + PSU GND
```

## 🚀 Installation

### Arduino
1. Install **FastLED** library in Arduino IDE
2. Upload `arduino/led_zeppelin.ino`
3. Connect hardware as shown above

### Raspberry Pi 5
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-gpiozero
   ```
2. Run the effects:
   ```bash
   sudo python3 raspi/party_mode.py
   ```

## ⚡ Effects Overview

| Effect | Arduino | Raspberry Pi | Description |
|--------|---------|--------------|-------------|
| Lightning Storm | ✅ | ✅ | Multiple lightning strikes across strip |
| Meteor Shower | ✅ | ✅ | Shooting meteors with fade trails |
| Fireworks | ✅ | ✅ | Rockets ascending + colorful explosions |
| Rainbow Chase | ✅ | ✅ | Smooth rainbow wave animation |
| Fire Simulation | ❌ | ✅ | Realistic fire with heat physics |
| Matrix Rain | ❌ | ✅ | Green code falling like Matrix |
| Wave Interference | ❌ | ✅ | Mathematical sine wave patterns |
| Police Lights | ✅ | ✅ | Red/blue alternating flash |
| Strobe | ✅ | ✅ | High-intensity white strobe |
| Confetti | ✅ | ✅ | Random colorful sparkles |

## 🎮 Usage

### Arduino
Effects run automatically in sequence. Upload code and enjoy the show!

### Raspberry Pi
```bash
cd /home/pi/led
sudo python3 raspi/party_mode.py
```

Press `Ctrl+C` to stop effects.

## ⚠️ Important Notes

### Power Supply
- **300 LEDs at full white:** ~18A current draw
- **Use external 5V PSU** for strips longer than 50 LEDs
- **Connect PSU ground** to controller ground

### Raspberry Pi 5 Specific
- **Raspberry Pi 5 only** - older Pi versions need different libraries
- **Must run with sudo** for GPIO access
- **GPIO18 required** - other pins may not work reliably

### Safety
- **Never exceed 5V** on WS2812B strips
- **Use proper gauge wire** for high current
- **Add capacitors** (1000μF) near LED strip for power stability

## 🏗️ Technical Details

### Arduino Implementation
- Uses **FastLED library** for hardware-optimized timing
- **Pin 6** provides perfect WS2812B signal timing
- All 300 LEDs controlled simultaneously

### Raspberry Pi Implementation  
- Uses **gpiozero** for Raspberry Pi 5 compatibility
- **Nanosecond-precision timing** for WS2812B protocol
- **Hardware GPIO control** bypasses Linux timing issues
- **Direct memory-mapped I/O** for maximum performance

### WS2812B Protocol
- **Data Format:** GRB (Green-Red-Blue) 24-bit per LED
- **Timing Critical:** 0.8μs/0.4μs for '1', 0.4μs/0.8μs for '0'  
- **Reset Signal:** >50μs low signal between frames

## 🐛 Troubleshooting

### Arduino Issues
- **No LEDs light up:** Check power supply and wiring
- **Wrong colors:** Verify LED strip is WS2812B (not WS2811)
- **Partial strip works:** Insufficient power supply

### Raspberry Pi Issues  
- **Permission denied:** Run with `sudo`
- **Only first ~150 LEDs work:** Use GPIO18, not other pins
- **Flickering:** Check power supply stability
- **Import errors:** Install `python3-gpiozero`

## 📊 Performance

| Platform | Max LEDs | Update Rate | CPU Usage |
|----------|----------|-------------|-----------|
| Arduino Uno | 300+ | 60 FPS | ~30% |
| Raspberry Pi 5 | 300+ | 100 FPS | ~15% |

## 🎨 Customization

### Adding New Effects
Both platforms use similar structure. For new effects:

1. **Arduino:** Add function, call in `loop()`
2. **Raspberry Pi:** Add function, call in `main()` loop

### Color Adjustment
- **Arduino:** Modify `BRIGHTNESS` constant (0-255)
- **Raspberry Pi:** Modify `BRIGHTNESS` variable (0.0-1.0)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Martin Pfeffer**  
- GitHub: [@pepperonas](https://github.com/pepperonas)

## 🙏 Acknowledgments

- **FastLED Community** for Arduino implementation
- **Raspberry Pi Foundation** for gpiozero library  
- **WS2812B Datasheet** for timing specifications

---

**⚡ Light up your world with LED Zeppelin! ⚡**