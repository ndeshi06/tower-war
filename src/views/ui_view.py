"""
UI View classes - thể hiện Observer Pattern và Template Method Pattern
"""
import pygame
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from ..models.base import Observer
from ..utils.constants import Colors, GameSettings, SCREEN_WIDTH, SCREEN_HEIGHT, GameState

class UIView(ABC):
    """
    Abstract base class cho UI views
    Thể hiện Template Method Pattern
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.font_cache = {}
    
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """
        Cache fonts để tối ưu performance
        Hỗ trợ tiếng Việt với Unicode fonts
        """
        key = (size, bold)
        if key not in self.font_cache:
            # List of fonts that support Vietnamese
            vietnamese_fonts = [
                'Times New Roman',  # Good Unicode support
                'Microsoft Sans Serif',  # Windows default, good Unicode
                'DejaVu Sans',  # Cross-platform, excellent Unicode
                'Segoe UI',  # Modern Windows font
                'Arial Unicode MS',  # If available
                'Arial'  # Fallback
            ]
            
            font_created = False
            for font_name in vietnamese_fonts:
                try:
                    self.font_cache[key] = pygame.font.SysFont(font_name, size, bold=bold)
                    font_created = True
                    break
                except:
                    continue
            
            if not font_created:
                # Ultimate fallback
                self.font_cache[key] = pygame.font.Font(None, size)
        return self.font_cache[key]
    
    def draw_text_with_shadow(self, screen: pygame.Surface, text: str, 
                            pos: Tuple[int, int], color: Tuple[int, int, int],
                            font: pygame.font.Font, shadow_offset: int = 2):
        """
        Vẽ text với shadow để dễ đọc hơn
        """
        # Draw shadow
        shadow = font.render(text, True, Colors.BLACK)
        shadow_pos = (pos[0] + shadow_offset, pos[1] + shadow_offset)
        screen.blit(shadow, shadow_pos)
        
        # Draw main text
        main_text = font.render(text, True, color)
        screen.blit(main_text, pos)
    
    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect, 
                   text: str, font: pygame.font.Font, 
                   bg_color: Tuple[int, int, int] = Colors.GRAY,
                   text_color: Tuple[int, int, int] = Colors.WHITE,
                   border_color: Tuple[int, int, int] = Colors.BLACK,
                   hover: bool = False):
        """
        Vẽ button với hiệu ứng hover
        """
        # Adjust color if hovering
        if hover:
            bg_color = tuple(min(255, c + 30) for c in bg_color)
        
        # Draw button background
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        
        # Draw button text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Abstract method để vẽ view"""
        pass
    
    def update_observer(self, event_type: str, data: dict):
        """Default implementation cho observer updates"""
        pass

class GameHUD(UIView, Observer):
    """
    Game HUD - hiển thị thông tin game
    """
    
    def __init__(self):
        super().__init__(0, 0, SCREEN_WIDTH, 120)
        Observer.__init__(self)
        self.game_stats = {}
        self.instructions_visible = True
    
    def update_observer(self, event_type: str, data: dict):
        """Update HUD khi có events"""
        if event_type == "game_stats_updated":
            self.game_stats = data
        elif event_type == "game_over":
            self.instructions_visible = False
    
    def draw(self, screen: pygame.Surface):
        """Vẽ HUD"""
        if not self.visible:
            return
        
        # Background cho HUD
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
        pygame.draw.rect(screen, (240, 240, 240), hud_rect)
        pygame.draw.rect(screen, Colors.BLACK, hud_rect, 2)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        self.draw_text_with_shadow(screen, "TOWER WAR", (20, 10), Colors.BLUE, title_font)
        
        # Instructions
        if self.instructions_visible:
            self._draw_instructions(screen)
        
        # Game stats
        self._draw_game_stats(screen)
    
    def _draw_instructions(self, screen: pygame.Surface):
        """Vẽ hướng dẫn chơi với tiếng Việt"""
        instruction_font = self.get_font(GameSettings.FONT_SMALL)
        instructions = [
            "• Nhấp vào tháp xanh để chọn",
            "• Nhấp vào tháp khác để gửi quân",
            "• Chiếm tất cả tháp để thắng"
        ]
        
        start_y = 50
        for i, instruction in enumerate(instructions):
            self.draw_text_with_shadow(screen, instruction, (20, start_y + i * 20), 
                                     Colors.BLACK, instruction_font, 1)
    
    def _draw_game_stats(self, screen: pygame.Surface):
        """Vẽ thống kê game"""
        if not self.game_stats:
            return
        
        stats_font = self.get_font(GameSettings.FONT_SMALL)
        
        # Player stats
        player_towers = self.game_stats.get('player_towers', 0)
        enemy_towers = self.game_stats.get('enemy_towers', 0)
        neutral_towers = self.game_stats.get('neutral_towers', 0)
        
        stats_text = [
            f"Player Towers: {player_towers}",
            f"Enemy Towers: {enemy_towers}",
            f"Neutral Towers: {neutral_towers}",
            f"Actions: {self.game_stats.get('player_actions', 0)}"
        ]
        
        start_x = SCREEN_WIDTH - 200
        start_y = 20
        
        for i, stat in enumerate(stats_text):
            color = Colors.BLUE if i == 0 else Colors.RED if i == 1 else Colors.GRAY if i == 2 else Colors.BLACK
            self.draw_text_with_shadow(screen, stat, (start_x, start_y + i * 20), 
                                     color, stats_font, 1)

class GameOverScreen(UIView, Observer):
    """
    Game Over screen
    """
    
    def __init__(self):
        super().__init__(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        Observer.__init__(self)
        self.winner = None
        self.game_stats = {}
        self.visible = False
        self.restart_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50)
        self.menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 170, 200, 50)
        self.mouse_pos = (0, 0)
    
    def update_observer(self, event_type: str, data: dict):
        """Update khi game over"""
        if event_type == "game_over":
            self.winner = data.get('winner')
            self.game_stats = data
            self.visible = True
        elif event_type == "game_restarted":
            self.visible = False
    
    def handle_click(self, pos: Tuple[int, int]) -> str:
        """
        Xử lý click vào buttons
        Returns: action name hoặc None
        """
        if self.restart_button.collidepoint(pos):
            return "restart"
        elif self.menu_button.collidepoint(pos):
            return "menu"
        return None
    
    def update_mouse_pos(self, pos: Tuple[int, int]):
        """Update mouse position cho hover effects"""
        self.mouse_pos = pos
    
    def draw(self, screen: pygame.Surface):
        """Vẽ game over screen"""
        if not self.visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 150, 500, 300)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Winner text
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        
        if self.winner == 'player':
            title_text = "BẠN THẮNG!"
            title_color = Colors.BLUE
        elif self.winner == 'enemy':
            title_text = "BẠN THUA!"
            title_color = Colors.RED
        else:
            title_text = "HÒA!"
            title_color = Colors.GRAY
        
        title_surface = title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect()
        title_pos = (SCREEN_WIDTH//2 - title_rect.width//2, SCREEN_HEIGHT//2 - 100)
        self.draw_text_with_shadow(screen, title_text, title_pos, title_color, title_font)
        
        # Game statistics
        self._draw_final_stats(screen)
        
        # Buttons
        restart_hover = self.restart_button.collidepoint(self.mouse_pos)
        menu_hover = self.menu_button.collidepoint(self.mouse_pos)
        
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        
        self.draw_button(screen, self.restart_button, "CHƠI LẠI", button_font,
                        Colors.GREEN, Colors.WHITE, Colors.BLACK, restart_hover)
        
        self.draw_button(screen, self.menu_button, "MENU", button_font,
                        Colors.GRAY, Colors.WHITE, Colors.BLACK, menu_hover)
    
    def _draw_final_stats(self, screen: pygame.Surface):
        """Vẽ thống kê cuối game"""
        if not self.game_stats:
            return
        
        stats_font = self.get_font(GameSettings.FONT_SMALL)
        
        duration_ms = self.game_stats.get('game_duration', 0)
        duration_sec = duration_ms // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        
        stats = [
            f"Thời gian: {minutes:02d}:{seconds:02d}",
            f"Hành động: {self.game_stats.get('player_actions', 0)}",
            f"Trận chiến: {self.game_stats.get('total_battles', 0)}",
        ]
        
        start_y = SCREEN_HEIGHT//2 - 30
        for i, stat in enumerate(stats):
            text_surface = stats_font.render(stat, True, Colors.BLACK)
            text_rect = text_surface.get_rect()
            text_pos = (SCREEN_WIDTH//2 - text_rect.width//2, start_y + i * 25)
            self.draw_text_with_shadow(screen, stat, text_pos, Colors.BLACK, stats_font, 1)

class PauseMenu(UIView, Observer):
    """
    Pause menu
    """
    
    def __init__(self):
        super().__init__(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        Observer.__init__(self)
        self.visible = False
        
        # Buttons
        button_width, button_height = 200, 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 100
        
        self.resume_button = pygame.Rect(center_x, start_y, button_width, button_height)
        self.restart_button = pygame.Rect(center_x, start_y + 70, button_width, button_height)
        self.menu_button = pygame.Rect(center_x, start_y + 140, button_width, button_height)
        
        self.mouse_pos = (0, 0)
    
    def update_observer(self, event_type: str, data: dict):
        """Update pause menu visibility"""
        if event_type == "game_paused":
            self.visible = True
        elif event_type == "game_resumed":
            self.visible = False
    
    def handle_click(self, pos: Tuple[int, int]) -> str:
        """Handle button clicks"""
        if not self.visible:
            return None
        
        if self.resume_button.collidepoint(pos):
            return "resume"
        elif self.restart_button.collidepoint(pos):
            return "restart"
        elif self.menu_button.collidepoint(pos):
            return "menu"
        return None
    
    def update_mouse_pos(self, pos: Tuple[int, int]):
        """Update mouse position"""
        self.mouse_pos = pos
    
    def draw(self, screen: pygame.Surface):
        """Draw pause menu"""
        if not self.visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150, 300, 300)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        title_text = "PAUSE"
        title_surface = title_font.render(title_text, True, Colors.BLACK)
        title_rect = title_surface.get_rect()
        title_pos = (SCREEN_WIDTH//2 - title_rect.width//2, SCREEN_HEIGHT//2 - 120)
        self.draw_text_with_shadow(screen, title_text, title_pos, Colors.BLACK, title_font)
        
        # Buttons
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        
        resume_hover = self.resume_button.collidepoint(self.mouse_pos)
        restart_hover = self.restart_button.collidepoint(self.mouse_pos)
        menu_hover = self.menu_button.collidepoint(self.mouse_pos)
        
        self.draw_button(screen, self.resume_button, "TIẾP TỤC", button_font,
                        Colors.GREEN, Colors.WHITE, Colors.BLACK, resume_hover)
        
        self.draw_button(screen, self.restart_button, "CHƠI LẠI", button_font,
                        Colors.BLUE, Colors.WHITE, Colors.BLACK, restart_hover)
        
        self.draw_button(screen, self.menu_button, "MENU", button_font,
                        Colors.GRAY, Colors.WHITE, Colors.BLACK, menu_hover)
