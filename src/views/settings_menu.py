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
        super().__init__(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Settings values
        self.ai_difficulty = "medium"
        self.sound_enabled = True
        self.music_enabled = True
        
        # Buttons
        button_width, button_height = 250, 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 100
        
        self.ai_easy_button = pygame.Rect(center_x - 200, start_y, 120, button_height)
        self.ai_medium_button = pygame.Rect(center_x - 60, start_y, 120, button_height)
        self.ai_hard_button = pygame.Rect(center_x + 80, start_y, 120, button_height)
        
        self.sound_button = pygame.Rect(center_x, start_y + 80, button_width, button_height)
        self.music_button = pygame.Rect(center_x, start_y + 140, button_width, button_height)
        self.back_button = pygame.Rect(center_x, start_y + 220, button_width, button_height)
        
        self.mouse_pos = (0, 0)
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """Handle settings button clicks"""
        if self.ai_easy_button.collidepoint(pos):
            self.ai_difficulty = "easy"
            return "ai_easy"
        elif self.ai_medium_button.collidepoint(pos):
            self.ai_difficulty = "medium"
            return "ai_medium"
        elif self.ai_hard_button.collidepoint(pos):
            self.ai_difficulty = "hard"
            return "ai_hard"
        elif self.sound_button.collidepoint(pos):
            self.sound_enabled = not self.sound_enabled
            return "toggle_sound"
        elif self.music_button.collidepoint(pos):
            self.music_enabled = not self.music_enabled
            return "toggle_music"
        elif self.back_button.collidepoint(pos):
            return "back"
        return None
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position"""
        self.mouse_pos = pos
    
    def draw(self, screen: pygame.Surface):
        """Vẽ settings menu"""
        if not self.visible:
            return
        
        # Background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 200, 600, 400)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        title_text = "CÀI ĐẶT"
        title_surface = title_font.render(title_text, True, Colors.BLACK)
        title_rect = title_surface.get_rect()
        title_pos = (SCREEN_WIDTH//2 - title_rect.width//2, SCREEN_HEIGHT//2 - 160)
        screen.blit(title_surface, title_pos)
        
        # AI Difficulty section
        self._draw_ai_difficulty(screen)
        
        # Audio settings
        self._draw_audio_settings(screen)
        
        # Back button
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        back_hover = self.back_button.collidepoint(self.mouse_pos)
        self.draw_button(screen, self.back_button, "QUAY LẠI", button_font,
                        Colors.GRAY, Colors.WHITE, Colors.BLACK, back_hover)
    
    def _draw_ai_difficulty(self, screen: pygame.Surface):
        """Vẽ AI difficulty settings"""
        label_font = self.get_font(GameSettings.FONT_MEDIUM)
        button_font = self.get_font(GameSettings.FONT_SMALL, bold=True)
        
        # Label
        label_text = "Độ khó AI:"
        label_surface = label_font.render(label_text, True, Colors.BLACK)
        screen.blit(label_surface, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 80))
        
        # Buttons
        difficulties = [
            (self.ai_easy_button, "DỄ", "easy"),
            (self.ai_medium_button, "TRUNG BÌNH", "medium"),
            (self.ai_hard_button, "KHÓ", "hard")
        ]
        
        for button_rect, text, difficulty in difficulties:
            is_selected = self.ai_difficulty == difficulty
            is_hover = button_rect.collidepoint(self.mouse_pos)
            
            bg_color = Colors.GREEN if is_selected else Colors.GRAY
            
            self.draw_button(screen, button_rect, text, button_font,
                           bg_color, Colors.WHITE, Colors.BLACK, is_hover)
    
    def _draw_audio_settings(self, screen: pygame.Surface):
        """Vẽ audio settings"""
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        
        # Sound button
        sound_text = f"ÂM THANH: {'BẬT' if self.sound_enabled else 'TẮT'}"
        sound_hover = self.sound_button.collidepoint(self.mouse_pos)
        sound_color = Colors.GREEN if self.sound_enabled else Colors.RED
        
        self.draw_button(screen, self.sound_button, sound_text, button_font,
                        sound_color, Colors.WHITE, Colors.BLACK, sound_hover)
        
        # Music button
        music_text = f"NHẠC NỀN: {'BẬT' if self.music_enabled else 'TẮT'}"
        music_hover = self.music_button.collidepoint(self.mouse_pos)
        music_color = Colors.GREEN if self.music_enabled else Colors.RED
        
        self.draw_button(screen, self.music_button, music_text, button_font,
                        music_color, Colors.WHITE, Colors.BLACK, music_hover)
