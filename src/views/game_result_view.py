"""
Game Result View - UI hiển thị kết quả game (win/lose)
"""
import pygame
from ..utils.constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, OwnerType

class GameResultView:
    """UI hiển thị kết quả game"""
    
    def __init__(self, screen=None):
        # Screen reference for scaling
        self.screen = screen
        
        # Initialize fonts với Unicode support
        pygame.font.init()
        try:
            # Sử dụng system font có hỗ trợ tiếng Việt
            self.font_title = pygame.font.SysFont('arial', 48, bold=True)
            self.font_subtitle = pygame.font.SysFont('arial', 32)
            self.font_button = pygame.font.SysFont('arial', 28)
        except:
            # Fallback với font mặc định
            self.font_title = pygame.font.Font(None, 48)
            self.font_subtitle = pygame.font.Font(None, 32)
            self.font_button = pygame.font.Font(None, 28)
        
        # Buttons
        self.buttons = {}
        self.hover_button = None
        
        # Animation
        self.animation_time = 0
        self.show_animation = True
        
    def setup_win_buttons(self, current_level, has_next_level, screen_width, screen_height):
        """Setup buttons cho trường hợp thắng"""
        self.buttons.clear()
        button_width = 200
        button_height = 60
        spacing = 20
        
        if has_next_level:
            # Next Level button
            x = screen_width // 2 - button_width // 2
            y = screen_height // 2 - 10
            next_level_text = f"Level {current_level + 1}"
            try:
                next_level_text = f"Level {current_level + 1}"
            except:
                next_level_text = "Next Level"
            
            self.buttons["next_level"] = {
                "rect": pygame.Rect(x, y, button_width, button_height),
                "text": next_level_text,
                "color": Colors.GREEN
            }
            
            # Main Menu button
            y += button_height + spacing
            self.buttons["main_menu"] = {
                "rect": pygame.Rect(x, y, button_width, button_height),
                "text": "Main Menu",
                "color": Colors.BLUE
            }
        else:
            # All levels complete - only main menu
            x = screen_width // 2 - button_width // 2
            y = screen_height // 2 - 10
            self.buttons["main_menu"] = {
                "rect": pygame.Rect(x, y, button_width, button_height),
                "text": "Main Menu",
                "color": Colors.BLUE
            }
    
    def setup_lose_buttons(self, screen_width, screen_height):
        """Setup buttons cho trường hợp thua"""
        self.buttons.clear()
        button_width = 200
        button_height = 60
        spacing = 20
        
        # Play Again button
        x = screen_width // 2 - button_width // 2
        y = screen_height // 2 - 10
        self.buttons["play_again"] = {
            "rect": pygame.Rect(x, y, button_width, button_height),
            "text": "Play Again",
            "color": Colors.GREEN
        }
        
        # Main Menu button
        y += button_height + spacing
        self.buttons["main_menu"] = {
            "rect": pygame.Rect(x, y, button_width, button_height),
            "text": "Main Menu",
            "color": Colors.BLUE
        }
    
    def handle_event(self, event):
        """Xử lý events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for action, button in self.buttons.items():
                    if button["rect"].collidepoint(event.pos):
                        return action
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hover_button = None
            for action, button in self.buttons.items():
                if button["rect"].collidepoint(event.pos):
                    self.hover_button = action
                    break
        
        return None
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
    
    def draw_win_screen(self, screen, current_level, has_next_level, all_complete=False):
        """Vẽ win screen"""
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 100, 0, 180))  # Green tint
        screen.blit(overlay, (0, 0))
        
        # Main container
        container_width = 400
        container_height = 300
        container_x = (screen_width - container_width) // 2
        container_y = (screen_height - container_height) // 2
        
        container_rect = pygame.Rect(container_x, container_y, container_width, container_height)
        pygame.draw.rect(screen, Colors.WHITE, container_rect)
        pygame.draw.rect(screen, Colors.GREEN, container_rect, 5)
        
        # Title
        if all_complete:
            title_text = "All Levels Complete!"
        else:
            title_text = f"Level {current_level} Complete!"
        
        title_surface = self.font_title.render(title_text, True, Colors.GREEN)
        title_rect = title_surface.get_rect(center=(container_x + container_width // 2, container_y + 60))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        if all_complete:
            subtitle_text = "You've conquered all challenges!"
        elif has_next_level:
            subtitle_text = f"Ready for Level {current_level + 1}?"
        else:
            subtitle_text = "Congratulations!"
        
        subtitle_surface = self.font_subtitle.render(subtitle_text, True, Colors.DARK_BLUE)
        subtitle_rect = subtitle_surface.get_rect(center=(container_x + container_width // 2, container_y + 100))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Setup buttons
        if all_complete:
            self.setup_win_buttons(current_level, False, screen_width, screen_height)
        else:
            self.setup_win_buttons(current_level, has_next_level, screen_width, screen_height)
        
        # Draw buttons
        self._draw_buttons(screen)
    
    def draw_lose_screen(self, screen, current_level):
        """Vẽ lose screen"""
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 180))  # Red tint
        screen.blit(overlay, (0, 0))
        
        # Main container
        container_width = 400
        container_height = 300
        container_x = (screen_width - container_width) // 2
        container_y = (screen_height - container_height) // 2
        
        container_rect = pygame.Rect(container_x, container_y, container_width, container_height)
        pygame.draw.rect(screen, Colors.WHITE, container_rect)
        pygame.draw.rect(screen, Colors.RED, container_rect, 5)
        
        # Title
        title_text = f"Level {current_level} Failed"
        title_surface = self.font_title.render(title_text, True, Colors.RED)
        title_rect = title_surface.get_rect(center=(container_x + container_width // 2, container_y + 60))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Try again?"
        subtitle_surface = self.font_subtitle.render(subtitle_text, True, Colors.DARK_BLUE)
        subtitle_rect = subtitle_surface.get_rect(center=(container_x + container_width // 2, container_y + 100))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Setup and draw buttons
        self.setup_lose_buttons(screen_width, screen_height)
        self._draw_buttons(screen)
    
    def _draw_buttons(self, screen):
        """Vẽ buttons"""
        for action, button in self.buttons.items():
            rect = button["rect"]
            text = button["text"]
            color = button["color"]
            
            is_hovered = self.hover_button == action
            
            # Button background
            bg_color = Colors.WHITE if not is_hovered else Colors.LIGHT_GRAY
            border_width = 3 if not is_hovered else 5
            
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, color, rect, border_width)
            
            # Button text
            text_surface = self.font_button.render(text, True, color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
    
    def reset_animation(self):
        """Reset animation state"""
        self.animation_time = 0
        self.show_animation = True
