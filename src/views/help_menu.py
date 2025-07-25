"""
Help Menu - hướng dẫn chơi game
"""
import pygame
from typing import Optional
from ..views.ui_view import UIView
from ..utils.constants import Colors, GameSettings, SCREEN_WIDTH, SCREEN_HEIGHT

class HelpMenu(UIView):
    """
    Help Menu class - hướng dẫn chơi
    """
    
    def __init__(self):
        super().__init__(0, 0, 1024, 576)  # Use default size, will be scaled dynamically
        
        # Back button - will be recalculated dynamically
        self.back_button = None
        self.mouse_pos = (0, 0)
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """Handle help menu clicks"""
        if self.back_button.collidepoint(pos):
            return "back"
        return None
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position"""
        self.mouse_pos = pos
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        self.back_button = pygame.Rect(screen_width//2 - 100, screen_height - 80, 200, 50)
    
    def draw(self, screen: pygame.Surface):
        """Vẽ help menu"""
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
        
        # Main panel
        panel_rect = pygame.Rect(50, 50, screen_width - 100, screen_height - 100)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        title_text = "HOW TO PLAY"
        title_surface = title_font.render(title_text, True, Colors.BLACK)
        title_rect = title_surface.get_rect()
        title_pos = (screen_width//2 - title_rect.width//2, 80)
        screen.blit(title_surface, title_pos)
        
        # Game rules
        self._draw_game_rules(screen)
        
        # Controls
        self._draw_controls(screen)
        
        # Back button
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        back_hover = self.back_button.collidepoint(self.mouse_pos)
        self.draw_button(screen, self.back_button, "BACK", button_font,
                        Colors.GRAY, Colors.WHITE, Colors.BLACK, back_hover)
    
    def _draw_game_rules(self, screen: pygame.Surface):
        """Vẽ luật chơi"""
        section_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        text_font = self.get_font(GameSettings.FONT_SMALL)
        
        # Section title
        section_title = "GAME RULES:"
        section_surface = section_font.render(section_title, True, Colors.BLUE)
        screen.blit(section_surface, (80, 140))
        
        # Rules
        rules = [
            "• Goal: Capture all enemy towers (red → blue or blue → red)",
            "• Blue towers: Yours (start with varying troops)",
            "• Red towers: AI's (start with 50% of your troops)", 
            "• Gray towers: Neutral (5-15 random troops)",
            "• Towers auto-generate 1 troop per second (max 50)",
            "• Send troops: Click blue tower → click target tower",
            "• Combat: Fewer troops eliminated, more troops reduced by difference",
            "• Troops on path can fight when meeting enemy troops"
        ]
        
        start_y = 170
        for i, rule in enumerate(rules):
            text_surface = text_font.render(rule, True, Colors.BLACK)
            screen.blit(text_surface, (100, start_y + i * 25))
    
    def _draw_controls(self, screen: pygame.Surface):
        """Vẽ điều khiển"""
        section_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        text_font = self.get_font(GameSettings.FONT_SMALL)
        
        # Section title
        section_title = "CONTROLS:"
        section_surface = section_font.render(section_title, True, Colors.BLUE)
        screen.blit(section_surface, (80, 380))
        
        # Controls
        controls = [
            "• Left mouse: Select tower and send troops",
            "• ESC: Pause game",
            "• R: Restart (when game over)",
            "• Space: Continue (when paused)"
        ]
        
        start_y = 410
        for i, control in enumerate(controls):
            text_surface = text_font.render(control, True, Colors.BLACK)
            screen.blit(text_surface, (100, start_y + i * 25))
