"""
Main Menu - menu chính của game
Thể hiện State Pattern và Template Method Pattern
"""
import pygame
from typing import Optional
from ..views.ui_view import UIView
from ..utils.constants import Colors, GameSettings, SCREEN_WIDTH, SCREEN_HEIGHT
from ..utils.image_manager import ImageManager

class MainMenu(UIView):
    """
    Main Menu class
    """
    
    def __init__(self):
        super().__init__(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Image manager
        self.image_manager = ImageManager()
        
        # Menu buttons - căn giữa chính xác
        button_width, button_height = 300, 60
        center_x = (SCREEN_WIDTH - button_width) // 2
        start_y = SCREEN_HEIGHT // 2 - 50
        
        self.start_button = pygame.Rect(center_x, start_y, button_width, button_height)
        self.settings_button = pygame.Rect(center_x, start_y + 80, button_width, button_height)
        self.help_button = pygame.Rect(center_x, start_y + 160, button_width, button_height)
        self.quit_button = pygame.Rect(center_x, start_y + 240, button_width, button_height)
        
        # Mouse position for hover effects
        self.mouse_pos = (0, 0)
        
        # Background
        self.background = None
        self._load_background()
    
    def _load_background(self):
        """Load background image hoặc tạo gradient background"""
        self.background = self.image_manager.get_image("background_menu")
        
        if not self.background:
            # Tạo gradient background nếu không có file
            self.background = self._create_gradient_background()
    
    def _create_gradient_background(self) -> pygame.Surface:
        """Tạo gradient background đẹp"""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Tạo gradient từ dark blue đến light blue
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Interpolate giữa dark blue và light blue
            r = int(Colors.DARK_BLUE[0] * (1 - ratio) + Colors.LIGHT_BLUE[0] * ratio)
            g = int(Colors.DARK_BLUE[1] * (1 - ratio) + Colors.LIGHT_BLUE[1] * ratio)
            b = int(Colors.DARK_BLUE[2] * (1 - ratio) + Colors.LIGHT_BLUE[2] * ratio)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        return surface
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """
        Handle menu button clicks
        Returns: action string hoặc None
        """
        if self.start_button.collidepoint(pos):
            return "start_game"
        elif self.settings_button.collidepoint(pos):
            return "settings"
        elif self.help_button.collidepoint(pos):
            return "help"
        elif self.quit_button.collidepoint(pos):
            return "quit"
        return None
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position cho hover effects"""
        self.mouse_pos = pos
    
    def draw(self, screen: pygame.Surface):
        """Vẽ main menu"""
        if not self.visible:
            return
        
        # Draw background
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(Colors.DARK_BLUE)
        
        # Draw title
        self._draw_title(screen)
        
        # Draw buttons
        self._draw_buttons(screen)
        
        # Draw footer
        self._draw_footer(screen)
    
    def _draw_title(self, screen: pygame.Surface):
        """Vẽ title của game"""
        title_font = self.get_font(72, bold=True)
        subtitle_font = self.get_font(24)
        
        # Main title
        title_text = "TOWER WAR"
        title_surface = title_font.render(title_text, True, Colors.WHITE)
        title_rect = title_surface.get_rect()
        title_pos = (SCREEN_WIDTH//2 - title_rect.width//2, 150)
        
        # Draw title with shadow
        self.draw_text_with_shadow(screen, title_text, title_pos, Colors.WHITE, title_font, 4)
        
        # Subtitle
        subtitle_text = "Classic Edition"
        subtitle_surface = subtitle_font.render(subtitle_text, True, Colors.LIGHT_BLUE)
        subtitle_rect = subtitle_surface.get_rect()
        subtitle_pos = (SCREEN_WIDTH//2 - subtitle_rect.width//2, title_pos[1] + title_rect.height + 10)
        
        self.draw_text_with_shadow(screen, subtitle_text, subtitle_pos, Colors.LIGHT_BLUE, subtitle_font, 2)
    
    def _draw_buttons(self, screen: pygame.Surface):
        """Vẽ menu buttons"""
        button_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        
        buttons = [
            (self.start_button, "START GAME", Colors.GREEN),
            (self.settings_button, "SETTINGS", Colors.BLUE),
            (self.help_button, "HELP", Colors.GRAY),
            (self.quit_button, "QUIT", Colors.RED)
        ]
        
        for button_rect, text, base_color in buttons:
            # Check hover
            hover = button_rect.collidepoint(self.mouse_pos)
            
            # Draw button với hover effect
            self.draw_button(
                screen, button_rect, text, button_font,
                bg_color=base_color,
                text_color=Colors.WHITE,
                border_color=Colors.BLACK,
                hover=hover
            )
    
    def _draw_footer(self, screen: pygame.Surface):
        """Vẽ footer với thông tin"""
        footer_font = self.get_font(GameSettings.FONT_SMALL)
        
        footer_texts = [
            "Use mouse to play",
            "ESC - Pause game",
            "Developed by Group 6 - OOP"
        ]
        
        start_y = SCREEN_HEIGHT - 80
        for i, text in enumerate(footer_texts):
            text_surface = footer_font.render(text, True, Colors.WHITE)
            text_rect = text_surface.get_rect()
            text_pos = (SCREEN_WIDTH//2 - text_rect.width//2, start_y + i * 20)
            
            self.draw_text_with_shadow(screen, text, text_pos, Colors.WHITE, footer_font, 1)
