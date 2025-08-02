#!/usr/bin/env python3

import numpy as np
import pyaudio
import threading
import time
import random
from collections import deque

class BeatDetector:
    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.channels = 1
        
        # Audio processing
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        
        # Beat detection parameters
        self.energy_history = deque(maxlen=20)  # Energy history for beat detection
        self.beat_threshold = 1.3  # Energy spike threshold
        self.min_beat_interval = 0.15  # Minimum time between beats (150ms)
        self.last_beat_time = 0
        
        # Current audio data
        self.current_energy = 0
        self.current_volume = 0
        self.current_freq_bands = [0, 0, 0, 0]  # Bass, Low-mid, High-mid, Treble
        self.beat_detected = False
        
        # Frequency band ranges (bass, low-mid, high-mid, treble)
        self.freq_ranges = [(60, 250), (250, 500), (500, 2000), (2000, 8000)]
        
        # Callbacks
        self.beat_callbacks = []
        self.audio_callbacks = []
    
    def _simple_bandpass(self, audio_data, low_freq, high_freq):
        """Simple frequency band extraction using FFT"""
        if len(audio_data) < 64:
            return 0
        
        # FFT analysis
        fft = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
        
        # Find frequency range indices
        low_idx = np.searchsorted(freqs, low_freq)
        high_idx = np.searchsorted(freqs, high_freq)
        
        # Extract energy in this band
        band_energy = np.sum(np.abs(fft[low_idx:high_idx]) ** 2)
        return band_energy
    
    def add_beat_callback(self, callback):
        """Add callback function to be called when beat is detected"""
        self.beat_callbacks.append(callback)
    
    def add_audio_callback(self, callback):
        """Add callback function to be called on every audio frame"""
        self.audio_callbacks.append(callback)
    
    def start(self, demo_mode=False):
        """Start audio capture and beat detection"""
        if self.running:
            return
        
        # Demo mode - simulate audio without microphone
        if demo_mode:
            print("🎵 Starting in DEMO MODE - no microphone required!")
            self.running = True
            # Start demo thread
            import threading
            demo_thread = threading.Thread(target=self._demo_mode_loop, daemon=True)
            demo_thread.start()
            return True
        
        try:
            # Find the best audio input device
            device_index = None
            device_info = None
            
            print(f"🎵 Scanning {self.audio.get_device_count()} audio devices...")
            
            # List all devices for debugging
            for i in range(self.audio.get_device_count()):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    device_name = info.get('name', '').lower()
                    max_inputs = info.get('maxInputChannels', 0)
                    print(f"   Device {i}: {info['name']} (inputs: {max_inputs})")
                    
                    # Prefer USB PnP Sound Device
                    if 'usb pnp sound device' in device_name and max_inputs > 0:
                        device_index = i
                        device_info = info
                        print(f"🎵 Selected USB audio device: {info['name']}")
                        break
                    # Fallback to any device with input channels
                    elif max_inputs > 0 and device_index is None:
                        device_index = i
                        device_info = info
                        print(f"🎵 Found potential device: {info['name']}")
                        
                except Exception as e:
                    print(f"   Device {i}: Error reading info - {e}")
                    continue
            
            if device_index is None:
                raise Exception("No suitable audio input device found")
            
            print(f"🎵 Using device {device_index}: {device_info['name']}")
            
            # Get device info for optimal settings
            device_info = self.audio.get_device_info_by_index(device_index)
            optimal_rate = int(device_info.get('defaultSampleRate', 44100))
            
            # Use device's preferred sample rate if different
            if optimal_rate != self.sample_rate:
                print(f"🎵 Adjusting sample rate from {self.sample_rate} to {optimal_rate}")
                self.sample_rate = optimal_rate
            
            # Try different configurations for better compatibility
            configs = [
                # Try with the detected device
                {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': self.sample_rate,
                    'input': True,
                    'input_device_index': device_index,
                    'frames_per_buffer': self.chunk_size
                },
                # Try with default device
                {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': self.sample_rate,
                    'input': True,
                    'frames_per_buffer': self.chunk_size
                },
                # Try with lower sample rate
                {
                    'format': self.format,
                    'channels': self.channels,
                    'rate': 22050,
                    'input': True,
                    'input_device_index': device_index,
                    'frames_per_buffer': self.chunk_size
                }
            ]
            
            stream_opened = False
            for i, config in enumerate(configs):
                try:
                    self.stream = self.audio.open(stream_callback=self._audio_callback, **config)
                    if 'rate' in config and config['rate'] != self.sample_rate:
                        print(f"🎵 Using sample rate: {config['rate']} Hz")
                        self.sample_rate = config['rate']
                    stream_opened = True
                    break
                except Exception as e:
                    print(f"❌ Audio config {i+1} failed: {e}")
                    continue
            
            if not stream_opened:
                raise Exception("Failed to open audio stream with any configuration")
            
            self.running = True
            self.stream.start_stream()
            print(f"🎵 Beat detector started successfully!")
            print(f"   Device: {device_info['name']}")
            print(f"   Sample Rate: {self.sample_rate} Hz")
            print(f"   Channels: {self.channels}")
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            print("💡 Try:")
            print("   - Check if your USB microphone is connected")
            print("   - Run: arecord -l")
            print("   - Test recording: arecord -D plughw:0,0 -f S16_LE -r 44100 -c 1 test.wav")
            return False
        
        return True
    
    def stop(self):
        """Stop audio capture with proper cleanup"""
        self.running = False
        
        # Give time for callbacks to finish
        time.sleep(0.1)
        
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            except Exception as e:
                print(f"Stream cleanup warning: {e}")
        
        # Terminate audio system
        try:
            if hasattr(self, 'audio') and self.audio:
                self.audio.terminate()
                self.audio = None
        except Exception as e:
            print(f"Audio termination warning: {e}")
        
        print("🔇 Beat detector stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Process audio data in real-time with error handling"""
        if not self.running:
            return (None, pyaudio.paComplete)
        
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize to [-1, 1]
            
            # Calculate overall energy and volume
            energy = np.sum(audio_data ** 2)
            volume = np.sqrt(np.mean(audio_data ** 2))
            
            self.current_energy = energy
            self.current_volume = volume
            
            # Frequency band analysis
            self.current_freq_bands = self._analyze_frequency_bands(audio_data)
            
            # Beat detection
            self.beat_detected = self._detect_beat(energy)
            
            # Call callbacks safely
            if self.beat_detected and self.running:
                for callback in self.beat_callbacks:
                    try:
                        if self.running:  # Check again before each callback
                            callback(energy, volume, self.current_freq_bands)
                    except Exception as e:
                        if self.running:
                            print(f"Beat callback error: {e}")
            
            if self.running:
                for callback in self.audio_callbacks:
                    try:
                        if self.running:  # Check again before each callback
                            callback(energy, volume, self.current_freq_bands, self.beat_detected)
                    except Exception as e:
                        if self.running:
                            print(f"Audio callback error: {e}")
                            
        except Exception as e:
            if self.running:
                print(f"Audio processing error: {e}")
        
        return (None, pyaudio.paContinue if self.running else pyaudio.paComplete)
    
    def _analyze_frequency_bands(self, audio_data):
        """Analyze energy in different frequency bands using FFT"""
        if len(audio_data) < 64:  # Too short for FFT
            return [0, 0, 0, 0]
        
        bands = []
        for low_freq, high_freq in self.freq_ranges:
            try:
                band_energy = self._simple_bandpass(audio_data, low_freq, high_freq)
                bands.append(band_energy)
            except:
                bands.append(0)
        
        return bands
    
    def _detect_beat(self, current_energy):
        """Simple beat detection based on energy spikes"""
        current_time = time.time()
        
        # Add current energy to history
        self.energy_history.append(current_energy)
        
        if len(self.energy_history) < 10:
            return False
        
        # Check minimum interval between beats
        if current_time - self.last_beat_time < self.min_beat_interval:
            return False
        
        # Calculate average energy
        avg_energy = np.mean(list(self.energy_history)[:-1])  # Exclude current
        
        # Detect beat if current energy significantly exceeds average
        if current_energy > avg_energy * self.beat_threshold and avg_energy > 0.001:
            self.last_beat_time = current_time
            return True
        
        return False
    
    def get_current_audio_info(self):
        """Get current audio analysis data"""
        return {
            'energy': self.current_energy,
            'volume': self.current_volume,
            'freq_bands': self.current_freq_bands,
            'beat_detected': self.beat_detected
        }
    
    def _demo_mode_loop(self):
        """Demo mode that simulates music beats and audio data"""
        import math
        print("🎵 Demo mode running - simulating music with 120 BPM")
        
        beat_interval = 60.0 / 120.0  # 120 BPM
        last_beat_time = 0
        
        while self.running:
            current_time = time.time()
            
            # Simulate audio data with sine waves
            t = current_time
            
            # Simulate frequency bands (bass, low-mid, high-mid, treble)
            bass = 0.3 + 0.7 * abs(math.sin(t * 2))
            low_mid = 0.2 + 0.6 * abs(math.sin(t * 3 + 1))
            high_mid = 0.1 + 0.5 * abs(math.sin(t * 5 + 2))
            treble = 0.05 + 0.4 * abs(math.sin(t * 7 + 3))
            
            self.current_freq_bands = [bass, low_mid, high_mid, treble]
            
            # Simulate volume and energy
            total_energy = sum(self.current_freq_bands)
            self.current_energy = total_energy
            self.current_volume = total_energy / 4
            
            # Simulate beats at 120 BPM
            beat_detected = False
            if current_time - last_beat_time >= beat_interval:
                beat_detected = True
                last_beat_time = current_time
                # Add some randomness to beat timing
                beat_interval = (60.0 / 120.0) + (random.random() - 0.5) * 0.1
            
            self.beat_detected = beat_detected
            
            # Call callbacks
            if beat_detected:
                for callback in self.beat_callbacks:
                    try:
                        callback(self.current_energy, self.current_volume, self.current_freq_bands)
                    except Exception as e:
                        print(f"Beat callback error: {e}")
            
            for callback in self.audio_callbacks:
                try:
                    callback(self.current_energy, self.current_volume, self.current_freq_bands, beat_detected)
                except Exception as e:
                    print(f"Audio callback error: {e}")
            
            time.sleep(0.05)  # 20 FPS
    
    def __del__(self):
        """Cleanup with error handling"""
        try:
            if hasattr(self, 'running') and self.running:
                self.stop()
        except:
            pass  # Ignore errors during cleanup

# Test the beat detector
if __name__ == "__main__":
    def on_beat(energy, volume, freq_bands):
        print(f"🥁 BEAT! Energy: {energy:.3f}, Volume: {volume:.3f}")
        print(f"   Bands: Bass={freq_bands[0]:.3f}, Low-mid={freq_bands[1]:.3f}, High-mid={freq_bands[2]:.3f}, Treble={freq_bands[3]:.3f}")
    
    def on_audio(energy, volume, freq_bands, beat):
        # Print audio info every 0.5 seconds
        if hasattr(on_audio, 'last_print'):
            if time.time() - on_audio.last_print < 0.5:
                return
        on_audio.last_print = time.time()
        
        beat_indicator = "🥁" if beat else "  "
        print(f"{beat_indicator} Vol: {volume:.3f} | Energy: {energy:.3f} | Bass: {freq_bands[0]:.3f}")
    
    detector = BeatDetector()
    detector.add_beat_callback(on_beat)
    detector.add_audio_callback(on_audio)
    
    print("🎵 Starting beat detection test...")
    print("Play some music and watch for beat detection!")
    print("Press Ctrl+C to stop")
    
    if detector.start():
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping beat detector...")
            detector.stop()
    else:
        print("❌ Failed to start beat detector")