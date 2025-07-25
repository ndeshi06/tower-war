import pygame
import os
from typing import Dict

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        pygame.mixer.init()  # Khởi tạo âm thanh
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sounds_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'sounds')
        self._initialized = True

    def play_background_music(self, filename="background_music.mp3", volume=1):
        path = os.path.join(self.sounds_folder, filename)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)  # -1 để phát lặp lại vô hạn
            print("[SoundManager] Background music started.")
        except pygame.error as e:
            print(f"[SoundManager] Failed to load background music: {e}")

    def load_sound(self, name: str, filename: str):
        """Load và cache âm thanh nếu chưa có"""
        if name not in self.sounds:
            path = os.path.join(self.sounds_folder, filename)
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"[SoundManager] Loaded sound: {filename}")
            except pygame.error as e:
                print(f"[SoundManager] Error loading {filename}: {e}")

    def play(self, name: str, volume: float = 1.0):
        """Play âm thanh theo tên"""
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound, maxtime=200)

    def preload(self):
        """Preload các âm thanh cần thiết"""
        self.load_sound("troop_add", "troop_add.wav")
        self.load_sound("troop_remove", "troop_remove.wav")
        self.load_sound("self_gain", "self_gain.wav")
        # Thêm các âm khác ở đây nếu cần

    def stop_all(self):
        pygame.mixer.stop()
