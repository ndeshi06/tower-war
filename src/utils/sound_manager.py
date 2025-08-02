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
        pygame.mixer.set_num_channels(32)  # Tăng số channel để hỗ trợ nhiều sound cùng lúc
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sounds_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'sounds')
        
        # Volume và mute controls
        self._master_volume = 1.0
        self._music_volume = 0.5
        self._sfx_volume = 0.7
        self._muted = False
        
        self._initialized = True

    @property
    def is_muted(self) -> bool:
        """Check if sound is muted"""
        return self._muted
    
    def set_muted(self, muted: bool):
        """Set mute state for all sounds"""
        self._muted = muted
        if muted:
            pygame.mixer.music.set_volume(0)
            # Mute all loaded sounds
            for sound in self.sounds.values():
                sound.set_volume(0)
        else:
            # Restore volumes
            pygame.mixer.music.set_volume(self._music_volume * self._master_volume)
            # Sounds will get their volume restored when played
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self._master_volume = max(0.0, min(1.0, volume))
        if not self._muted:
            pygame.mixer.music.set_volume(self._music_volume * self._master_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0) and update currently playing music"""
        self._music_volume = max(0.0, min(1.0, volume))
        # Update currently playing music volume
        final_volume = self._music_volume * self._master_volume
        pygame.mixer.music.set_volume(final_volume)
        print(f"[SoundManager] Music volume set to {self._music_volume} (final: {final_volume})")
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self._sfx_volume = max(0.0, min(1.0, volume))
        print(f"[SoundManager] SFX volume set to {self._sfx_volume}")

    def is_music_playing(self):
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()
    
    def get_current_music_file(self):
        """Get currently playing music file name (we'll track this)"""
        return getattr(self, '_current_music_file', None)
    
    def _set_current_music_file(self, filename):
        """Internal method to track current music file"""
        self._current_music_file = filename

    def play_background_music(self, filename="background_music.mp3", volume=None):
        """Play background music for menus"""
        # Don't restart if same music is already playing
        if self.is_music_playing() and self.get_current_music_file() == filename:
            print(f"[SoundManager] Background music {filename} already playing, continuing...")
            return
            
        if volume is None:
            volume = self._music_volume
        
        path = os.path.join(self.sounds_folder, filename)
        try:
            pygame.mixer.music.load(path)
            # Music volume calculation - only affected by music_volume and master_volume
            final_volume = volume * self._master_volume
            pygame.mixer.music.set_volume(final_volume)
            pygame.mixer.music.play(-1)  # -1 để phát lặp lại vô hạn
            self._set_current_music_file(filename)
            print(f"[SoundManager] Background music started. Volume: {final_volume}")
        except pygame.error as e:
            print(f"[SoundManager] Failed to load background music: {e}")

    def play_gameview_music(self, filename="gameview_music.mp3", volume=None):
        """Play music for game view"""
        # Don't restart if same music is already playing
        if self.is_music_playing() and self.get_current_music_file() == filename:
            print(f"[SoundManager] Gameview music {filename} already playing, continuing...")
            return
            
        if volume is None:
            volume = self._music_volume
        
        path = os.path.join(self.sounds_folder, filename)
        try:
            pygame.mixer.music.load(path)
            # Music volume calculation - only affected by music_volume and master_volume
            final_volume = volume * self._master_volume
            pygame.mixer.music.set_volume(final_volume)
            pygame.mixer.music.play(-1)  # -1 để phát lặp lại vô hạn
            self._set_current_music_file(filename)
            print(f"[SoundManager] Gameview music started. Volume: {final_volume}")
        except pygame.error as e:
            print(f"[SoundManager] Failed to load gameview music: {e}")

    def play_intro_music(self, filename="sound_intro.mp3", volume=None):
        """Play music for intro screen"""
        # Don't restart if same music is already playing
        if self.is_music_playing() and self.get_current_music_file() == filename:
            print(f"[SoundManager] Intro music {filename} already playing, continuing...")
            return
            
        if volume is None:
            volume = self._music_volume
        
        path = os.path.join(self.sounds_folder, filename)
        try:
            pygame.mixer.music.load(path)
            # Music volume calculation - only affected by music_volume and master_volume
            final_volume = volume * self._master_volume
            pygame.mixer.music.set_volume(final_volume)
            pygame.mixer.music.play(-1)  # -1 để phát lặp lại vô hạn
            self._set_current_music_file(filename)
            print(f"[SoundManager] Intro music started. Volume: {final_volume}")
        except pygame.error as e:
            print(f"[SoundManager] Failed to load intro music: {e}")

    def load_sound(self, name: str, filename: str):
        """Load và cache âm thanh nếu chưa có"""
        if name not in self.sounds:
            path = os.path.join(self.sounds_folder, filename)
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"[SoundManager] Loaded sound: {filename}")
            except pygame.error as e:
                print(f"[SoundManager] Error loading {filename}: {e}")

    def play(self, name: str, volume: float = None):
        """Play âm thanh theo tên với volume control - chỉ bị ảnh hưởng bởi SFX volume"""
        sound = self.sounds.get(name)
        if sound:
            if volume is None:
                volume = self._sfx_volume
            
            # SFX volume = 0 means muted, otherwise use normal volume calculation
            if self._sfx_volume == 0:
                return  # Don't play SFX if SFX volume is 0
            
            final_volume = volume * self._master_volume
            sound.set_volume(final_volume)
            
            # Tìm channel trống hoặc tạo mới để không bị đè lên nhau
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)  # Bỏ maxtime để sound không bị cắt
            else:
                # Nếu không có channel trống, phát trực tiếp (pygame sẽ tự quản lý)
                sound.play()

    def preload(self):
        """Preload các âm thanh cần thiết"""
        self.load_sound("troop_add", "troop_add.wav")
        self.load_sound("troop_remove", "troop_remove.wav")
        self.load_sound("self_gain", "self_gain.wav")
        self.load_sound("tower_destroy", "tower_destroy.wav")  # Sound khi tower bị capture
        # Thêm các âm khác ở đây nếu cần

    def stop_all(self):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
