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
        super().__init__(0, 0, 1024, 576)  # Use default size, will be scaled dynamically

        # Background (phải khởi tạo trước)
        self.background = None
        # Image manager
        self.image_manager = ImageManager()
        self._load_background()

        # Menu buttons - will be recalculated dynamically
        self.start_button = None
        self.settings_button = None
        self.help_button = None
        self.quit_button = None
        self.continue_button = None  # Thêm thuộc tính này
        self.new_game_button = None  # Thêm thuộc tính này

        # Mouse position for hover effects
        self.mouse_pos = (0, 0)

        # Trạng thái có progression không
        self.has_progression = self._check_progression()

    def _check_progression(self):
        """Kiểm tra có file save progression không"""
        import os
        from ..utils.progression_manager import ProgressionManager
        pm = ProgressionManager()
        return os.path.exists(pm.save_path)
        
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
        # Chỉ cho click CONTINUE nếu có progression
        if self.continue_button and self.continue_button.collidepoint(pos):
            if self.has_progression:
                return "continue_game"
            else:
                return None
        elif self.new_game_button and self.new_game_button.collidepoint(pos):
            return "new_game"
        elif self.settings_button and self.settings_button.collidepoint(pos):
            return "settings"
        elif self.help_button and self.help_button.collidepoint(pos):
            return "help"
        elif self.quit_button and self.quit_button.collidepoint(pos):
            return "quit"
        return None
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        # Menu buttons - căn giữa chính xác và đẩy lên cao hơn để tránh footer
        button_width, button_height = 300, 60
        center_x = (screen_width - button_width) // 2
        start_y = screen_height // 2 - 150  # Đẩy lên cao hơn để đủ chỗ cho 5 nút

        self.continue_button = pygame.Rect(center_x, start_y, button_width, button_height)
        self.new_game_button = pygame.Rect(center_x, start_y + 80, button_width, button_height)
        self.settings_button = pygame.Rect(center_x, start_y + 160, button_width, button_height)
        self.help_button = pygame.Rect(center_x, start_y + 240, button_width, button_height)
        self.quit_button = pygame.Rect(center_x, start_y + 320, button_width, button_height)
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position cho hover effects"""
        self.mouse_pos = pos
    
    def draw(self, screen: pygame.Surface):
        """Vẽ main menu"""
        if not self.visible:
            return

        # Luôn cập nhật trạng thái progression trước khi vẽ
        self.has_progression = self._check_progression()

        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Recalculate button positions for current screen size
        self._recalculate_buttons(screen_width, screen_height)

        # Draw background
        if self.background:
            # Scale background to fit screen
            scaled_bg = pygame.transform.scale(self.background, (screen_width, screen_height))
            screen.blit(scaled_bg, (0, 0))
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
        screen_width = screen.get_width()
        
        title_font = self.get_font(72, bold=True)
        # Main title
        title_text = "TOWER WAR"
        title_surface = title_font.render(title_text, True, Colors.WHITE)
        title_rect = title_surface.get_rect()
        title_pos = (screen_width//2 - title_rect.width//2, 60)
        # Draw title with shadow
        self.draw_text_with_shadow(screen, title_text, title_pos, Colors.WHITE, title_font, 4)
    
    def _draw_buttons(self, screen: pygame.Surface):
        """Vẽ menu buttons với Continue và New Game"""
        button_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        buttons = [
            (self.continue_button, "CONTINUE", Colors.ORANGE, not self.has_progression),
            (self.new_game_button, "NEW GAME", Colors.GREEN, False),
            (self.settings_button, "SETTINGS", Colors.BLUE, False),
            (self.help_button, "HELP", Colors.GRAY, False),
            (self.quit_button, "QUIT", Colors.RED, False)
        ]
        for button_rect, text, base_color, disabled in buttons:
            hover = button_rect.collidepoint(self.mouse_pos) and not disabled
            draw_color = Colors.LIGHT_GRAY if disabled else base_color
            self.draw_button(
                screen, button_rect, text, button_font,
                bg_color=draw_color,
                text_color=Colors.WHITE,
                border_color=Colors.BLACK,
                hover=hover
            )
    
    def _draw_footer(self, screen: pygame.Surface):
        """Vẽ footer với thông tin và version"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        footer_font = self.get_font(GameSettings.FONT_SMALL)
        version_font = self.get_font(24)
        
        footer_texts = [
            "Use mouse to play • F11 - Toggle Fullscreen", 
            "Developed by Group 6 - 24C06 HCMUS",
        ]
        # Đặt footer ở cuối màn hình, tránh đè lên button
        footer_start_y = screen_height - 50
        for i, text in enumerate(footer_texts):
            text_surface = footer_font.render(text, True, Colors.WHITE)
            text_rect = text_surface.get_rect()
            text_pos = (screen_width//2 - text_rect.width//2, footer_start_y + i * 20)
            self.draw_text_with_shadow(screen, text, text_pos, Colors.WHITE, footer_font, 1)

        # Vẽ version ở góc trái dưới
        version_text = "Version 1.0"
        version_surface = version_font.render(version_text, True, Colors.LIGHT_BLUE)
        version_rect = version_surface.get_rect()
        version_pos = (16, screen_height - version_rect.height - 10)
        self.draw_text_with_shadow(screen, version_text, version_pos, Colors.LIGHT_BLUE, version_font, 2)
