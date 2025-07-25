"""
Settings Menu - menu cài đặt
"""
import pygame
from typing import Optional
from ..views.ui_view import UIView
from ..utils.constants import Colors, GameSettings, SCREEN_WIDTH, SCREEN_HEIGHT

class SettingsMenu(UIView):
    """
    Settings Menu class
    """
    
    def __init__(self):
        super().__init__(0, 0, 1024, 576)  # Use default size, will be scaled dynamically
        
        # Settings values
        self.sound_enabled = True
        self.music_enabled = True
        
        # Buttons - will be recalculated dynamically
        self.sound_button = None
        self.music_button = None
        self.back_button = None
        
        self.mouse_pos = (0, 0)
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """Handle settings button clicks"""
        print(f"Settings click at: {pos}")
        
        # Make sure buttons are calculated
        if not self.sound_button:
            screen_width, screen_height = 1024, 576  # Default size
            self._recalculate_buttons(screen_width, screen_height)
        
        print(f"Sound button: {self.sound_button}")
        print(f"Music button: {self.music_button}")
        print(f"Back button: {self.back_button}")
        print(f"Current sound_enabled: {self.sound_enabled}")
        print(f"Current music_enabled: {self.music_enabled}")
        
        if self.sound_button and self.sound_button.collidepoint(pos):
            old_state = self.sound_enabled
            self.sound_enabled = not self.sound_enabled
            print(f"Sound toggled from {old_state} to: {self.sound_enabled}")
            return "toggle_sound"
        elif self.music_button and self.music_button.collidepoint(pos):
            old_state = self.music_enabled
            self.music_enabled = not self.music_enabled
            print(f"Music toggled from {old_state} to: {self.music_enabled}")
            return "toggle_music"
        elif self.back_button and self.back_button.collidepoint(pos):
            print("Back button clicked")
            return "back"
        
        print("No button clicked")
        return None
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position"""
        self.mouse_pos = pos
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        # Buttons - căn giữa chính xác
        button_width, button_height = 250, 50
        center_x = screen_width // 2
        start_y = screen_height // 2 - 30  # Căn giữa thật sự
        
        # Other buttons - căn giữa
        self.sound_button = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        self.music_button = pygame.Rect(center_x - button_width // 2, start_y + 70, button_width, button_height)
        self.back_button = pygame.Rect(center_x - button_width // 2, start_y + 140, button_width, button_height)
    
    def draw(self, screen: pygame.Surface):
        """Vẽ settings menu"""
        if not self.visible:
            return
        
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Recalculate button positions
        self._recalculate_buttons(screen_width, screen_height)
        
        # Background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel - căn giữa đúng cách
        panel_rect = pygame.Rect(screen_width//2 - 200, screen_height//2 - 120, 400, 240)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        title_text = "SETTINGS"
        title_surface = title_font.render(title_text, True, Colors.BLACK)
        title_rect = title_surface.get_rect()
        title_pos = (screen_width//2 - title_rect.width//2, screen_height//2 - 90)
        screen.blit(title_surface, title_pos)
        
        # Audio settings
        self._draw_audio_settings(screen)
        
        # Back button
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        back_hover = self.back_button.collidepoint(self.mouse_pos)
        self.draw_button(screen, self.back_button, "BACK", button_font,
                        Colors.GRAY, Colors.WHITE, Colors.BLACK, back_hover)
    
    def _draw_audio_settings(self, screen: pygame.Surface):
        """Vẽ audio settings"""
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        
        # Sound button
        sound_text = f"SOUND: {'ON' if self.sound_enabled else 'OFF'}"
        sound_hover = self.sound_button.collidepoint(self.mouse_pos)
        sound_color = Colors.GREEN if self.sound_enabled else Colors.RED
        
        self.draw_button(screen, self.sound_button, sound_text, button_font,
                        sound_color, Colors.WHITE, Colors.BLACK, sound_hover)
        
        # Music button
        music_text = f"MUSIC: {'ON' if self.music_enabled else 'OFF'}"
        music_hover = self.music_button.collidepoint(self.mouse_pos)
        music_color = Colors.GREEN if self.music_enabled else Colors.RED
        
        self.draw_button(screen, self.music_button, music_text, button_font,
                        music_color, Colors.WHITE, Colors.BLACK, music_hover)
