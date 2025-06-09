# ResourceManager.py
import pygame
import os

class ResourceManager:
    def __init__(self):
        self.sounds = {}
        self.images = {}
        self.fonts = {}
        self.base_path = os.path.dirname(__file__)
        self.sounds_path = os.path.join(self.base_path, "sounds")
        self.images_path = os.path.join(self.base_path, "images")
        self.fonts_path = os.path.join(self.base_path, "fonts")

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