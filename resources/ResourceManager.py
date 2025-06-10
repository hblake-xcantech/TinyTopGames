# ResourceManager.py
import pygame
import os
import requests
import threading
import queue
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")

class ResourceManager:
    def __init__(self, audio_ready_callback=None, audio_failed_callback=None):
        self.sounds = {}
        self.images = {}
        self.fonts = {}
        self.voices = {}
        self.base_path = os.path.dirname(__file__)
        self.sounds_path = os.path.join(self.base_path, "sounds")
        self.images_path = os.path.join(self.base_path, "images")
        self.fonts_path = os.path.join(self.base_path, "fonts")
        self.voice_path = os.path.join(self.base_path, "voice")
        
        # Create voice directory if it doesn't exist
        Path(self.voice_path).mkdir(exist_ok=True)
        
        # Voice generation system
        self.voice_queue = queue.Queue()
        self.voice_cache = {}
        self.voice_lock = threading.Lock()
        self.voice_worker_running = False
        self.audio_ready_callback = audio_ready_callback
        self.audio_failed_callback = audio_failed_callback
        
        # ElevenLabs settings
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_name = 'Annie'
        self.voice_id = None
        
        # Start voice worker if API key is available
        if self.api_key:
            self._start_voice_worker()
        else:
            print("⚠️ ELEVENLABS_API_KEY not found in environment variables")

    def play_sound(self, name):
        if name not in self.sounds:
            self._load_sound(name)
        if name in self.sounds:
            self.sounds[name].play()

    def _load_sound(self, name):
        path_wav = os.path.join(self.sounds_path, f"{name}.wav")
        path_ogg = os.path.join(self.sounds_path, f"{name}.ogg")
        
        # Debug: print the paths being checked
        print(f"Looking for sound '{name}' in:")
        print(f"  WAV: {path_wav}")
        print(f"  OGG: {path_ogg}")
        
        if os.path.exists(path_wav):
            print(f"✓ Loading WAV: {path_wav}")
            self.sounds[name] = pygame.mixer.Sound(path_wav)
        elif os.path.exists(path_ogg):
            print(f"✓ Loading OGG: {path_ogg}")
            self.sounds[name] = pygame.mixer.Sound(path_ogg)
        else:
            print(f"⚠️ Sound not found: {name}")
            print(f"   Searched in: {self.sounds_path}")

    # (Optional) extend later:
    def load_image(self, name):
        if name not in self.images:
            path = os.path.join(self.images_path, f"{name}.png")
            if os.path.exists(path):
                self.images[name] = pygame.image.load(path).convert_alpha()
            else:
                print(f"⚠️ Image not found: {name}")
        return self.images.get(name)

    def load_font(self, name, size):
        key = f"{name}_{size}"
        if key not in self.fonts:
            path = os.path.join(self.fonts_path, f"{name}.ttf")
            if os.path.exists(path):
                self.fonts[key] = pygame.font.Font(path, size)
            else:
                print(f"⚠️ Font not found: {name}")
        return self.fonts.get(key)
    
    def get_sound_path(self, name):
        """Get the full path to a sound file for manual loading (e.g., pygame.mixer.music)"""
        path_wav = os.path.join(self.sounds_path, f"{name}.wav")
        path_ogg = os.path.join(self.sounds_path, f"{name}.ogg")
        
        if os.path.exists(path_wav):
            return path_wav
        elif os.path.exists(path_ogg):
            return path_ogg
        else:
            print(f"⚠️ Sound path not found: {name}")
            return None
    
    def _start_voice_worker(self):
        """Start the background voice generation worker"""
        if not self.voice_worker_running and self.api_key:
            self.voice_worker_running = True
            self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.voice_thread.start()
            print("🎤 Voice worker started")
    
    def _get_voice_id(self):
        """Get the voice ID for the specified voice name"""
        if self.voice_id:
            return self.voice_id
            
        try:
            headers = {'xi-api-key': self.api_key}
            response = requests.get('https://api.elevenlabs.io/v1/voices', headers=headers)
            response.raise_for_status()
            voices = response.json()
            
            for voice in voices['voices']:
                if voice['name'].lower() == self.voice_name.lower():
                    self.voice_id = voice['voice_id']
                    print(f"✓ Found voice '{self.voice_name}': {self.voice_id}")
                    return self.voice_id
            
            # Fallback to first voice
            self.voice_id = voices['voices'][0]['voice_id']
            print(f"⚠️ Voice '{self.voice_name}' not found, using default: {self.voice_id}")
            return self.voice_id
            
        except Exception as e:
            print(f"❌ Error getting voice ID: {e}")
            return None
    
    def _voice_worker(self):
        """Background worker for generating voice audio"""
        voice_id = self._get_voice_id()
        if not voice_id:
            return
            
        while True:
            try:
                word = self.voice_queue.get(timeout=1)
                if word is None:  # Shutdown signal
                    break
                
                print(f"🎤 Generating voice for: {word}")
                
                # Check if already exists
                voice_file = os.path.join(self.voice_path, f"{word}.wav")
                if os.path.exists(voice_file):
                    print(f"✓ Voice already exists: {word}")
                    with self.voice_lock:
                        self.voice_cache[word] = voice_file
                    
                    # Notify job system that audio is ready (even if it already existed)
                    if self.audio_ready_callback:
                        self.audio_ready_callback(word)
                    
                    self.voice_queue.task_done()
                    continue
                
                # Generate voice using ElevenLabs API
                url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
                headers = {
                    'xi-api-key': self.api_key,
                    'Content-Type': 'application/json',
                    'Accept': 'audio/wav'
                }
                data = {
                    'text': word,
                    'model_id': 'eleven_multilingual_v2',
                    'voice_settings': {
                        'stability': 0.8,  # Slightly faster generation
                        'similarity_boost': 0.8
                    }
                }
                
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                # Save the audio file
                with open(voice_file, 'wb') as f:
                    f.write(response.content)
                
                with self.voice_lock:
                    self.voice_cache[word] = voice_file
                
                print(f"✓ Generated voice: {word}")
                
                # Notify job system that audio is ready
                if self.audio_ready_callback:
                    self.audio_ready_callback(word)
                
                self.voice_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error generating voice for '{word}': {e}")
                # Notify job system that audio failed
                if self.audio_failed_callback:
                    self.audio_failed_callback(word)
                self.voice_queue.task_done()
    
    def play_voice(self, word):
        """Play a voice for the given word. Generates if not available."""
        if not self.api_key:
            print("⚠️ ElevenLabs API key not available")
            return False
            
        word = word.lower().strip()
        voice_file = os.path.join(self.voice_path, f"{word}.wav")
        
        # Check if file exists locally
        if os.path.exists(voice_file):
            try:
                if word not in self.voices:
                    self.voices[word] = pygame.mixer.Sound(voice_file)
                self.voices[word].play()
                print(f"🔊 Playing voice: {word}")
                return True
            except Exception as e:
                print(f"❌ Error playing voice '{word}': {e}")
                return False
        
        # Check cache
        with self.voice_lock:
            if word in self.voice_cache:
                try:
                    if word not in self.voices:
                        self.voices[word] = pygame.mixer.Sound(self.voice_cache[word])
                    self.voices[word].play()
                    print(f"🔊 Playing cached voice: {word}")
                    return True
                except Exception as e:
                    print(f"❌ Error playing cached voice '{word}': {e}")
        
        # Queue for generation if not available
        print(f"🎤 Queueing voice generation: {word}")
        self.voice_queue.put(word)
        return False
    
    def preload_voice(self, word):
        """Queue a word for voice generation without playing"""
        if not self.api_key:
            return
            
        word = word.lower().strip()
        voice_file = os.path.join(self.voice_path, f"{word}.wav")
        
        # Only queue if not already available
        if not os.path.exists(voice_file):
            with self.voice_lock:
                if word not in self.voice_cache:
                    print(f"🎤 Preloading voice: {word}")
                    self.voice_queue.put(word)
    
    def preload_voices(self, words):
        """Preload multiple voices"""
        for word in words:
            self.preload_voice(word)