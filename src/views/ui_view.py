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
        self.screen = None  # Screen reference for scaling
    
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
                            font: pygame.font.Font, shadow_offset: int = 2, 
                            shadow_color: Tuple[int, int, int] = None):
        """
        Vẽ text với shadow để dễ đọc hơn
        """
        if shadow_color is None:
            shadow_color = Colors.BLACK
            
        # Draw shadow
        shadow = font.render(text, True, shadow_color)
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
        super().__init__(0, 0, SCREEN_WIDTH, 80)  # Giảm từ 120 xuống 80
        Observer.__init__(self)
        self.game_stats = {}
        self.instructions_visible = True
        self.level_info = ""
        self.level_progress = ""
    
    def update_observer(self, event_type: str, data: dict):
        """Update HUD khi có events"""
        if event_type == "game_stats_updated":
            self.game_stats = data
        elif event_type == "game_over":
            self.instructions_visible = False
        elif event_type == "game_restarted":
            self.instructions_visible = True
            self.level_info = data.get('level_info', '')
            self.level_progress = data.get('progress', f"Level {data.get('level', 1)}/3")
        elif event_type == "level_started":
            self.level_info = data.get('level_info', '')
            self.level_progress = data.get('progress', f"Level {data.get('level', 1)}/3")
        elif event_type == "level_changed":
            self.level_info = data.get('level_info', '')
            self.level_progress = data.get('progress', f"Level {data.get('level', 1)}/3")
    
    def draw(self, screen: pygame.Surface):
        """Vẽ HUD"""
        if not self.visible:
            return
        
        # Get current screen dimensions
        screen_width = screen.get_width()
        
        # Background cho HUD
        hud_rect = pygame.Rect(0, 0, screen_width, 80)  # Giảm chiều cao
        pygame.draw.rect(screen, (240, 240, 240), hud_rect)
        pygame.draw.rect(screen, Colors.BLACK, hud_rect, 2)
        
        # Title
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        self.draw_text_with_shadow(screen, "TOWER WAR", (20, 10), Colors.BLUE, title_font)
        
        # Level info - display in top right corner with better visibility
        if self.level_progress:
            level_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
            
            # Calculate right-aligned position
            level_text = self.level_progress
            level_surface = level_font.render(level_text, True, Colors.WHITE)
            level_x = screen_width - level_surface.get_width() - 20
            
            # Background box for better visibility
            bg_padding = 10
            bg_width = level_surface.get_width() + bg_padding * 2
            bg_height = 40  # Reduced height since no difficulty text
            bg_rect = pygame.Rect(level_x - bg_padding, 10, bg_width, bg_height)
            
            # Draw background with border
            pygame.draw.rect(screen, Colors.DARK_BLUE, bg_rect)
            pygame.draw.rect(screen, Colors.WHITE, bg_rect, 2)
            
            # Draw level number with white text on dark background
            self.draw_text_with_shadow(screen, level_text, (level_x, 15), Colors.WHITE, level_font, shadow_color=Colors.BLACK)
        
        # Instructions
        if self.instructions_visible:
            self._draw_instructions(screen)
        
        # Game stats
        self._draw_game_stats(screen)
    
    def _draw_instructions(self, screen: pygame.Surface):
        """Draw game instructions in English - compact"""
        instruction_font = self.get_font(GameSettings.FONT_SMALL)
        instructions = [
            "• Click blue tower → Click other tower to send troops • Capture all red towers to win",
        ]
        
        start_y = 45
        for i, instruction in enumerate(instructions):
            self.draw_text_with_shadow(screen, instruction, (20, start_y + i * 15), 
                                     Colors.BLACK, instruction_font, 1)
    
    def _draw_game_stats(self, screen: pygame.Surface):
        """Vẽ thống kê game"""
        if not self.game_stats:
            return
        
        screen_width = screen.get_width()
        stats_font = self.get_font(GameSettings.FONT_SMALL)
        
        # Player stats
        player_towers = self.game_stats.get('player_towers', 0)
        enemy_towers = self.game_stats.get('enemy_towers', 0)
        neutral_towers = self.game_stats.get('neutral_towers', 0)
        
        stats_text = [
            f"Player: {player_towers}",
            f"Enemy: {enemy_towers}",
            f"Neutral: {neutral_towers}"
        ]
        
        start_x = screen_width - 200
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
        super().__init__(0, 0, 1024, 576)  # Default size, will be recalculated dynamically
        Observer.__init__(self)
        self.winner = None
        self.game_stats = {}
        self.visible = False
        self.is_level_complete = False
        self.next_level_info = ""
        self.all_levels_complete = False
        
        # Buttons - will be recalculated dynamically
        self.restart_button = None
        self.menu_button = None
        self.next_level_button = None
        self.mouse_pos = (0, 0)
    
    def update_observer(self, event_type: str, data: dict):
        """Update khi game over hoặc level complete"""
        if event_type == "game_over":
            self.winner = data.get('winner')
            self.game_stats = data
            self.visible = True
            self.is_level_complete = False
            self.all_levels_complete = False
        elif event_type == "level_complete":
            self.winner = data.get('winner')
            self.game_stats = data
            self.visible = True
            self.is_level_complete = True
            self.next_level_info = data.get('next_level_info', '')
            self.all_levels_complete = False
        elif event_type == "all_levels_complete":
            self.winner = data.get('winner')
            self.game_stats = data
            self.visible = True
            self.is_level_complete = False
            self.all_levels_complete = True
        elif event_type == "game_restarted":
            self.visible = False
            self.is_level_complete = False
            self.all_levels_complete = False
    
    def handle_click(self, pos: Tuple[int, int]) -> str:
        """
        Xử lý click vào buttons
        Returns: action name hoặc None
        """
        # Make sure buttons are calculated
        if not self.restart_button:
            # Use default screen size if not available
            screen_width, screen_height = 1024, 576
            self._recalculate_buttons(screen_width, screen_height)
        
        if self.is_level_complete and self.next_level_button and self.next_level_button.collidepoint(pos):
            return "restart"  # Start next level
        elif self.restart_button.collidepoint(pos):
            return "restart"
        elif self.menu_button.collidepoint(pos):
            return "menu"
        return None
    
    def update_mouse_pos(self, pos: Tuple[int, int]):
        """Update mouse position cho hover effects"""
        self.mouse_pos = pos
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        self.restart_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 100, 200, 50)
        self.menu_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 170, 200, 50)
        self.next_level_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 50, 200, 50)
    
    def draw(self, screen: pygame.Surface):
        """Vẽ game over screen"""
        if not self.visible:
            return
        
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Recalculate button positions
        self._recalculate_buttons(screen_width, screen_height)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(screen_width//2 - 250, screen_height//2 - 150, 500, 300)
        pygame.draw.rect(screen, Colors.WHITE, panel_rect)
        pygame.draw.rect(screen, Colors.BLACK, panel_rect, 3)
        
        # Winner text và level info
        title_font = self.get_font(GameSettings.FONT_LARGE, bold=True)
        
        if self.all_levels_complete:
            title_text = "Congratulations! All levels completed!"
            title_color = Colors.BLUE
        elif self.is_level_complete:
            title_text = "Congratulations! Level completed!"
            title_color = Colors.BLUE
        elif self.winner == 'player':
            title_text = "YOU WIN!"
            title_color = Colors.BLUE
        elif self.winner == 'enemy':
            title_text = "YOU LOSE!"
            title_color = Colors.RED
        else:
            title_text = "DRAW!"
            title_color = Colors.GRAY
        
        title_surface = title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect()
        title_pos = (screen_width//2 - title_rect.width//2, screen_height//2 - 100)
        self.draw_text_with_shadow(screen, title_text, title_pos, title_color, title_font)
        
        # Next level info
        if self.is_level_complete and self.next_level_info:
            info_font = self.get_font(GameSettings.FONT_MEDIUM)
            info_text = f"Next: {self.next_level_info}"
            info_pos = (screen_width//2 - 150, screen_height//2 - 60)
            self.draw_text_with_shadow(screen, info_text, info_pos, Colors.BLACK, info_font)
        
        # Game statistics
        self._draw_final_stats(screen)
        
        # Buttons
        button_font = self.get_font(GameSettings.FONT_MEDIUM, bold=True)
        
        if self.is_level_complete:
            # Level complete buttons
            next_hover = self.next_level_button.collidepoint(self.mouse_pos)
            menu_hover = self.menu_button.collidepoint(self.mouse_pos)
            
            self.draw_button(screen, self.next_level_button, "NEXT LEVEL", button_font,
                            Colors.GREEN, Colors.WHITE, Colors.BLACK, next_hover)
            
            self.draw_button(screen, self.menu_button, "MAIN MENU", button_font,
                            Colors.GRAY, Colors.WHITE, Colors.BLACK, menu_hover)
        else:
            # Normal game over buttons
            restart_hover = self.restart_button.collidepoint(self.mouse_pos)
            menu_hover = self.menu_button.collidepoint(self.mouse_pos)
            
            restart_text = "RESTART LEVEL 1" if self.winner == 'enemy' else "RESTART"
            
            self.draw_button(screen, self.restart_button, restart_text, button_font,
                            Colors.GREEN, Colors.WHITE, Colors.BLACK, restart_hover)
            
            self.draw_button(screen, self.menu_button, "MAIN MENU", button_font,
                            Colors.GRAY, Colors.WHITE, Colors.BLACK, menu_hover)
    
    def _draw_final_stats(self, screen: pygame.Surface):
        """Vẽ thống kê cuối game"""
        if not self.game_stats:
            return
        
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        stats_font = self.get_font(GameSettings.FONT_SMALL)
        
        duration_ms = self.game_stats.get('game_duration', 0)
        duration_sec = duration_ms // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        
        stats = [
            f"Duration: {minutes:02d}:{seconds:02d}"
        ]
        
        start_y = screen_height//2 - 30
        for i, stat in enumerate(stats):
            text_surface = stats_font.render(stat, True, Colors.BLACK)
            text_rect = text_surface.get_rect()
            text_pos = (screen_width//2 - text_rect.width//2, start_y + i * 25)
            self.draw_text_with_shadow(screen, stat, text_pos, Colors.BLACK, stats_font, 1)

class PauseMenu(UIView, Observer):
    """
    Pause menu
    """
    
    def __init__(self):
        super().__init__(0, 0, 1024, 576)  # Default size, will be recalculated dynamically
        Observer.__init__(self)
        self.visible = False
        
        # Sound settings - get from menu manager
        self.sound_enabled = True
        self.music_enabled = True
        
        # Buttons - will be recalculated dynamically
        self.resume_button = None
        self.restart_button = None
        self.menu_button = None
        self.sound_button = None
        self.music_button = None
        
        self.mouse_pos = (0, 0)
    
    def update_observer(self, event_type: str, data: dict):
        """Update pause menu visibility"""
        if event_type == "game_paused":
            self.visible = True
            # Sync sound settings from menu manager
            if hasattr(data, 'menu_manager'):
                menu_manager = data['menu_manager']
                self.sound_enabled = menu_manager.is_sound_enabled()
                self.music_enabled = menu_manager.is_music_enabled()
        elif event_type == "game_resumed":
            self.visible = False
    
    def handle_click(self, pos: Tuple[int, int]) -> str:
        """Handle button clicks"""
        if not self.visible:
            return None
        
        # Make sure buttons are calculated
        if not self.resume_button:
            # Use default screen size if not available
            screen_width, screen_height = 1024, 576
            self._recalculate_buttons(screen_width, screen_height)
        
        if self.resume_button.collidepoint(pos):
            return "resume"
        elif self.restart_button.collidepoint(pos):
            return "restart"
        elif self.menu_button.collidepoint(pos):
            return "menu"
        elif self.sound_button.collidepoint(pos):
            return "toggle_sound"
        elif self.music_button.collidepoint(pos):
            return "toggle_music"
        return None
    
    def update_mouse_pos(self, pos: Tuple[int, int]):
        """Update mouse position"""
        self.mouse_pos = pos
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        # Buttons - làm lớn hơn và thêm sound controls
        button_width, button_height = 250, 60  # Tăng từ 200x50 lên 250x60
        center_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 120  # Điều chỉnh vị trí bắt đầu để có chỗ cho sound controls
        
        self.resume_button = pygame.Rect(center_x, start_y, button_width, button_height)
        self.restart_button = pygame.Rect(center_x, start_y + 80, button_width, button_height)
        self.menu_button = pygame.Rect(center_x, start_y + 160, button_width, button_height)
        
        # Sound control buttons - wider to fit text
        sound_button_width, sound_button_height = 160, 50  # Tăng từ 140 lên 160 để chữ không bị tràn
        sound_start_x = screen_width // 2 - 165  # Adjust position to center both buttons
        sound_y = start_y + 240
        
        self.sound_button = pygame.Rect(sound_start_x, sound_y, sound_button_width, sound_button_height)
        self.music_button = pygame.Rect(sound_start_x + 170, sound_y, sound_button_width, sound_button_height)  # Tăng spacing từ 150 lên 170
    
    def draw(self, screen: pygame.Surface):
        """Draw pause menu"""
        if not self.visible:
            return
        
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Recalculate button positions
        self._recalculate_buttons(screen_width, screen_height)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)  # Tăng độ mờ
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Main panel với shadow - làm lớn hơn để chứa sound controls
        shadow_rect = pygame.Rect(screen_width//2 - 202, screen_height//2 - 222, 404, 444)
        panel_rect = pygame.Rect(screen_width//2 - 200, screen_height//2 - 220, 400, 440)
        
        # Draw shadow
        pygame.draw.rect(screen, Colors.BLACK, shadow_rect, border_radius=10)
        
        # Draw main panel với gradient effect
        pygame.draw.rect(screen, Colors.WHITE, panel_rect, border_radius=10)
        pygame.draw.rect(screen, Colors.DARK_BLUE, panel_rect, 3, border_radius=10)
        
        # Title - tăng font size
        title_font = self.get_font(48, bold=True)  # Tăng từ 36 lên 48
        title_text = "GAME PAUSED"
        title_surface = title_font.render(title_text, True, Colors.DARK_BLUE)
        title_rect = title_surface.get_rect()
        title_pos = (screen_width//2 - title_rect.width//2, screen_height//2 - 180)
        self.draw_text_with_shadow(screen, title_text, title_pos, Colors.DARK_BLUE, title_font)
        # Buttons với animation - tăng font size
        button_font = self.get_font(28, bold=True)  # Tăng từ 24 lên 28
        
        resume_hover = self.resume_button.collidepoint(self.mouse_pos)
        restart_hover = self.restart_button.collidepoint(self.mouse_pos)
        menu_hover = self.menu_button.collidepoint(self.mouse_pos)
        sound_hover = self.sound_button.collidepoint(self.mouse_pos)
        music_hover = self.music_button.collidepoint(self.mouse_pos)
        
        # Resume button - màu xanh lá
        self.draw_button(screen, self.resume_button, "CONTINUE", button_font,
                        Colors.GREEN if not resume_hover else Colors.LIGHT_GREEN, 
                        Colors.WHITE, Colors.BLACK, resume_hover)
        
        # Restart button - màu xanh dương
        self.draw_button(screen, self.restart_button, "RESTART", button_font,
                        Colors.BLUE if not restart_hover else Colors.LIGHT_BLUE, 
                        Colors.WHITE, Colors.BLACK, restart_hover)
        
        # Menu button - màu xám
        self.draw_button(screen, self.menu_button, "MAIN MENU", button_font,
                        Colors.GRAY if not menu_hover else Colors.LIGHT_GRAY, 
                        Colors.WHITE, Colors.BLACK, menu_hover)
        
        # Sound control buttons - smaller font
        sound_button_font = self.get_font(22, bold=True)
        
        # Sound button
        sound_text = f"SFX: {'ON' if self.sound_enabled else 'OFF'}"
        sound_color = Colors.GREEN if self.sound_enabled else Colors.RED
        sound_hover_color = Colors.LIGHT_GREEN if self.sound_enabled else Colors.LIGHT_RED
        
        self.draw_button(screen, self.sound_button, sound_text, sound_button_font,
                        sound_color if not sound_hover else sound_hover_color, 
                        Colors.WHITE, Colors.BLACK, sound_hover)
        
        # Music button
        music_text = f"MUSIC: {'ON' if self.music_enabled else 'OFF'}"
        music_color = Colors.GREEN if self.music_enabled else Colors.RED
        music_hover_color = Colors.LIGHT_GREEN if self.music_enabled else Colors.LIGHT_RED
        
        self.draw_button(screen, self.music_button, music_text, sound_button_font,
                        music_color if not music_hover else music_hover_color, 
                        Colors.WHITE, Colors.BLACK, music_hover)
        
        # Controls hint - tăng font size và update
        hint_font = self.get_font(18)  # Tăng từ 16 lên 18
        hint_text = "ESC or SPACE to continue"
        hint_surface = hint_font.render(hint_text, True, Colors.GRAY)
        hint_rect = hint_surface.get_rect()
        hint_pos = (screen_width//2 - hint_rect.width//2, screen_height//2 + 180)  # Điều chỉnh vị trí xuống dưới
        screen.blit(hint_surface, hint_pos)
