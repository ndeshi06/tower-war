"""
Level Selection View - UI cho chọn level
"""
import pygame
from ..utils.constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, GameSettings

class LevelSelectView:
    """UI cho việc chọn level"""
    
    def __init__(self):
        # Initialize fonts với Unicode support
        pygame.font.init()
        try:
            # Sử dụng system font có hỗ trợ tiếng Việt
            self.font_title = pygame.font.SysFont('arial', 48, bold=True)
            self.font_button = pygame.font.SysFont('arial', 32)
            self.font_desc = pygame.font.SysFont('arial', 24)
        except:
            # Fallback với font mặc định
            self.font_title = pygame.font.Font(None, 48)
            self.font_button = pygame.font.Font(None, 32)
            self.font_desc = pygame.font.Font(None, 24)
        
        # Level buttons
        self.level_buttons = []
        self.back_button = None
        self.setup_buttons()
        
        # Animation
        self.hover_button = None
        self.animation_time = 0
        
    def setup_buttons(self):
        """Setup level buttons"""
        button_width = 250
        button_height = 90
        spacing = 40
        
        # Tính toán để căn giữa toàn bộ nhóm buttons
        total_height = 3 * button_height + 2 * spacing
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        levels = [
            {"name": "Level 1", "desc": "Easy - 3 vs 2", "difficulty": "Easy"},
            {"name": "Level 2", "desc": "Medium - 2 vs 3", "difficulty": "Medium"},
            {"name": "Level 3", "desc": "Hard - 2 vs 4", "difficulty": "Hard"}
        ]
        
        for i, level in enumerate(levels):
            # Căn giữa chính xác theo chiều ngang
            x = (SCREEN_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.level_buttons.append({
                "rect": button_rect,
                "level": i + 1,
                "name": level["name"],
                "desc": level["desc"],
                "difficulty": level["difficulty"]
            })
        
        # Back button
        back_x = 50
        back_y = SCREEN_HEIGHT - 100
        self.back_button = pygame.Rect(back_x, back_y, 120, 50)
    
    def handle_event(self, event):
        """Xử lý events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check level buttons
                for button in self.level_buttons:
                    if button["rect"].collidepoint(event.pos):
                        return f"level_{button['level']}"
                
                # Check back button
                if self.back_button.collidepoint(event.pos):
                    return "back_to_menu"
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hover_button = None
            for button in self.level_buttons:
                if button["rect"].collidepoint(event.pos):
                    self.hover_button = button
                    break
            
            if self.back_button.collidepoint(event.pos):
                self.hover_button = "back"
        
        return None
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
    
    def draw(self, screen):
        """Vẽ level selection screen"""
        # Background
        screen.fill(Colors.LIGHT_BLUE)
        
        # Title - căn giữa và cách từ top
        title_text = self.font_title.render("Select Level", True, Colors.DARK_BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Level buttons
        for button in self.level_buttons:
            self._draw_level_button(screen, button)
        
        # Back button
        self._draw_back_button(screen)
    
    def _draw_level_button(self, screen, button):
        """Vẽ level button"""
        rect = button["rect"]
        is_hovered = self.hover_button == button
        
        # Button background
        color = Colors.WHITE if not is_hovered else Colors.LIGHT_GREEN
        border_color = Colors.DARK_BLUE if not is_hovered else Colors.GREEN
        border_width = 3 if not is_hovered else 5
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, border_color, rect, border_width)
        
        # Level name
        name_text = self.font_button.render(button["name"], True, Colors.DARK_BLUE)
        name_rect = name_text.get_rect(center=(rect.centerx, rect.centery - 15))
        screen.blit(name_text, name_rect)
        
        # Description
        desc_text = self.font_desc.render(button["desc"], True, Colors.DARK_BLUE)
        desc_rect = desc_text.get_rect(center=(rect.centerx, rect.centery + 10))
        screen.blit(desc_text, desc_rect)
        
        # Difficulty
        diff_text = self.font_desc.render(f"Difficulty: {button['difficulty']}", True, Colors.RED)
        diff_rect = diff_text.get_rect(center=(rect.centerx, rect.centery + 30))
        screen.blit(diff_text, diff_rect)
    
    def _draw_back_button(self, screen):
        """Vẽ back button"""
        is_hovered = self.hover_button == "back"
        
        color = Colors.LIGHT_GRAY if not is_hovered else Colors.WHITE
        border_color = Colors.BLACK if not is_hovered else Colors.DARK_BLUE
        border_width = 2 if not is_hovered else 3
        
        pygame.draw.rect(screen, color, self.back_button)
        pygame.draw.rect(screen, border_color, self.back_button, border_width)
        
        # Text
        text = self.font_button.render("← Menu", True, Colors.BLACK)
        text_rect = text.get_rect(center=self.back_button.center)
        screen.blit(text, text_rect)
