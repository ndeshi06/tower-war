"""
Game View - Main rendering class
Thể hiện MVC Pattern và Observer Pattern
"""
import pygame
from typing import List
from ..models.base import Observer
from ..models.tower import Tower
from ..models.troop import Troop
from ..views.ui_view import GameHUD, GameOverScreen, PauseMenu
from ..utils.constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, GameState

class GameView(Observer):
    """
    Main game view class - responsible for rendering all game objects
    Thể hiện Observer Pattern - quan sát game state changes
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background_color = Colors.WHITE
        
        # Load background image
        from ..utils.image_manager import ImageManager
        self.image_manager = ImageManager()
        self.background_image = self.image_manager.get_image("background_game")
        
        # UI Components
        self.hud = GameHUD()
        self.game_over_screen = GameOverScreen()
        self.pause_menu = PauseMenu()
        
        # Game state
        self.game_state = GameState.PLAYING
        self.towers: List[Tower] = []
        self.troops: List[Troop] = []
        
        # Visual effects
        self.selection_pulse_time = 0
        self.show_grid = False
        
        # Level complete dialog
        self.show_level_complete_dialog = False
        self.level_complete_data = None
        self._level_complete_surface = None  # Cache the dialog surface
        
        # Performance optimization
        self.dirty_rects = []
    
    def update_observer(self, event_type: str, data: dict):
        """
        Implementation của Observer interface
        Update view khi có game state changes
        """
        if event_type == "game_state_changed":
            self.game_state = data.get('new_state', GameState.PLAYING)
            print(f"GameView: Game state changed to {self.game_state}")
        
        elif event_type == "towers_updated":
            self.towers = data.get('towers', [])
        
        elif event_type == "troops_updated":
            self.troops = data.get('troops', [])
        
        elif event_type == "game_over":
            self.game_state = GameState.GAME_OVER  
            self.game_over_screen.update_observer(event_type, data)
            # Reset level complete dialog
            self.show_level_complete_dialog = False
            self.level_complete_data = None
            print(f"GameView: Game over! Winner: {data.get('winner')}")
        
        elif event_type == "level_complete":
            self.game_state = GameState.LEVEL_COMPLETE
            self.show_level_complete_dialog = True
            self.level_complete_data = data
            self._level_complete_surface = None  # Reset cached surface
            # Don't show game over screen for level complete
            print(f"GameView: Level complete! Next: {data.get('next_level_info')}")
        
        elif event_type == "all_levels_complete":
            self.game_state = GameState.GAME_OVER
            self.game_over_screen.update_observer(event_type, data)
            # Reset level complete dialog
            self.show_level_complete_dialog = False
            self.level_complete_data = None
            print("GameView: All levels completed!")
        
        elif event_type == "game_restarted":
            self.game_over_screen.update_observer(event_type, data)
            # Reset game view state
            self.game_state = GameState.PLAYING
            self.pause_menu.visible = False
            level_info = data.get('level_info', '')
            print(f"GameView: Game restarted - {level_info}")
        
        elif event_type == "game_stats_updated":
            self.hud.update_observer(event_type, data)
        
        # Forward pause/resume events to pause menu
        elif event_type == "game_paused":
            self.pause_menu.update_observer(event_type, data)
            print("GameView: Game paused - showing pause menu")
        
        elif event_type == "game_resumed":
            self.pause_menu.update_observer(event_type, data)
            print("GameView: Game resumed - hiding pause menu")
        
        # Handle level started (ẩn level complete dialog)
        elif event_type == "level_started":
            self.game_state = GameState.PLAYING
            self.show_level_complete_dialog = False
            self.level_complete_data = None
            self._level_complete_surface = None  # Clear cached surface
            print(f"GameView: Level {data.get('level', '')} started - {data.get('level_info', '')}")
            self.level_complete_data = None
            print(f"GameView: Level {data.get('level', '')} started - {data.get('level_info', '')}")
    
    def set_towers(self, towers: List[Tower]):
        """Update towers list"""
        self.towers = towers
    
    def set_troops(self, troops: List[Troop]):
        """Update troops list"""
        self.troops = troops
    
    def update_hud_stats(self, stats: dict):
        """Update HUD with game statistics"""
        self.hud.update_observer("game_stats_updated", stats)
    
    def update_mouse_position(self, pos):
        """Update mouse position cho UI hover effects"""
        self.game_over_screen.update_mouse_pos(pos)
        self.pause_menu.update_mouse_pos(pos)
    
    def handle_ui_click(self, pos) -> str:
        """
        Handle clicks on UI elements
        Returns: action name hoặc None
        """
        # Check game over screen
        if self.game_over_screen.visible:
            return self.game_over_screen.handle_click(pos)
        
        # Check pause menu
        if self.pause_menu.visible:
            return self.pause_menu.handle_click(pos)
        
        return None
    
    def show_pause_menu(self):
        """Show pause menu"""
        self.pause_menu.visible = True
    
    def hide_pause_menu(self):
        """Hide pause menu"""
        self.pause_menu.visible = False
    
    def toggle_grid(self):
        """Toggle grid display"""
        self.show_grid = not self.show_grid
    
    def draw(self, dt: float):
        """
        Main draw method
        Template Method Pattern - định nghĩa skeleton của rendering process
        """
        # Clear screen
        self._clear_screen()
        
        # Draw background elements
        self._draw_background()
        
        # Draw game objects
        self._draw_game_objects(dt)
        
        # Draw UI
        self._draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def _clear_screen(self):
        """Clear screen với background color hoặc background image"""
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.background_color)
    
    def _draw_background(self):
        """Draw background elements như grid"""
        if self.show_grid:
            self._draw_grid()
    
    def _draw_grid(self):
        """Draw grid để debug hoặc visual aid"""
        grid_size = 50
        grid_color = (230, 230, 230)
        
        # Vertical lines
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        
        # Horizontal lines
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    
    def _draw_game_objects(self, dt: float):
        """Draw all game objects"""
        # Update selection pulse effect
        self.selection_pulse_time += dt
        
        # Draw towers
        self._draw_towers()
        
        # Draw troops
        self._draw_troops()
        
        # Draw connections for selected tower
        self._draw_tower_connections()
    
    def _draw_towers(self):
        """Draw all towers"""
        for tower in self.towers:
            if tower.active:
                tower.draw(self.screen)
                
                # Draw additional effects for selected tower
                if tower.selected:
                    self._draw_selection_effect(tower)
    
    def _draw_selection_effect(self, tower: Tower):
        """
        Draw selection effect cho selected tower
        Animated pulse effect
        """
        import math
        
        # Pulse effect
        pulse_factor = (math.sin(self.selection_pulse_time * 5) + 1) / 2  # 0-1
        pulse_radius = tower.radius + 5 + (pulse_factor * 10)
        
        # Draw pulsing circle
        alpha = int(100 + (pulse_factor * 100))  # 100-200
        
        # Create surface with alpha
        pulse_surface = pygame.Surface((pulse_radius * 4, pulse_radius * 4))
        pulse_surface.set_alpha(alpha)
        pulse_surface.fill(Colors.WHITE)
        
        pygame.draw.circle(pulse_surface, Colors.BLUE, 
                         (pulse_radius * 2, pulse_radius * 2), 
                         int(pulse_radius), 3)
        
        # Blit pulse surface
        pulse_rect = pulse_surface.get_rect(center=(tower.x, tower.y))
        self.screen.blit(pulse_surface, pulse_rect)
    
    def _draw_troops(self):
        """Draw all troops"""
        for troop in self.troops:
            if troop.active:
                troop.draw(self.screen)
                
                # Draw movement trail
                self._draw_troop_trail(troop)
    
    def _draw_troop_trail(self, troop: Troop):
        """
        Draw trail effect cho moving troops
        """
        # Simple trail effect - draw line from current position towards start
        trail_length = 20
        trail_color = tuple(c // 2 for c in troop.get_color())  # Darker version
        
        # Calculate trail start position
        import math
        target_x, target_y = troop.target_position
        distance_total = math.sqrt((target_x - troop.x)**2 + (target_y - troop.y)**2)
        
        if distance_total > 0:
            # Normalize direction
            dx = (target_x - troop.x) / distance_total
            dy = (target_y - troop.y) / distance_total
            
            # Trail start position
            trail_start_x = troop.x - dx * trail_length
            trail_start_y = troop.y - dy * trail_length
            
            # Draw trail line
            pygame.draw.line(self.screen, trail_color,
                           (trail_start_x, trail_start_y),
                           (troop.x, troop.y), 2)
    
    def _draw_tower_connections(self):
        """
        Draw connections từ selected tower đến các towers khác
        """
        selected_tower = None
        for tower in self.towers:
            if tower.selected:
                selected_tower = tower
                break
        
        if selected_tower is None:
            return
        
        # Draw lines đến các towers khác
        for tower in self.towers:
            if tower != selected_tower and tower.active:
                # Different colors based on ownership
                if tower.owner == selected_tower.owner:
                    line_color = Colors.GREEN
                elif tower.owner == 'neutral':
                    line_color = Colors.GRAY
                else:
                    line_color = Colors.RED
                
                # Draw dashed line
                self._draw_dashed_line(self.screen, line_color,
                                     (selected_tower.x, selected_tower.y),
                                     (tower.x, tower.y), 2, 10)
    
    def _draw_dashed_line(self, surface: pygame.Surface, color, start_pos, end_pos, 
                         width: int = 1, dash_length: int = 5):
        """
        Draw dashed line
        """
        import math
        
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calculate distance and direction
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distance == 0:
            return
        
        # Normalize direction
        dx = (x2 - x1) / distance
        dy = (y2 - y1) / distance
        
        # Draw dashes
        current_distance = 0
        draw_dash = True
        
        while current_distance < distance:
            # Calculate dash end position
            dash_end_distance = min(current_distance + dash_length, distance)
            
            if draw_dash:
                start_x = x1 + dx * current_distance
                start_y = y1 + dy * current_distance
                end_x = x1 + dx * dash_end_distance
                end_y = y1 + dy * dash_end_distance
                
                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)
            
            current_distance = dash_end_distance
            draw_dash = not draw_dash
    
    def _draw_ui(self):
        """Draw all UI elements"""
        # Draw HUD
        self.hud.draw(self.screen)
        
        # Priority order: Pause menu > Level complete > Game over
        if self.game_state == GameState.PAUSED:
            # Draw pause menu if paused (highest priority)
            self.pause_menu.draw(self.screen)
        elif self.show_level_complete_dialog and self.level_complete_data and self.game_state == GameState.LEVEL_COMPLETE:
            # Draw level complete dialog only if in level complete state
            self._draw_level_complete_dialog()
        elif self.game_state == GameState.GAME_OVER:
            # Draw game over screen only if game ended and no level complete dialog
            self.game_over_screen.draw(self.screen)
    
    def _draw_level_complete_dialog(self):
        """Vẽ dialog khi hoàn thành level"""
        # Create dialog surface only once to prevent flickering
        if self._level_complete_surface is None:
            # Create a surface for the entire dialog
            self._level_complete_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% alpha
            self._level_complete_surface.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 400
            dialog_height = 200
            dialog_x = (SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
            
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(self._level_complete_surface, Colors.WHITE, dialog_rect)
            pygame.draw.rect(self._level_complete_surface, Colors.BLACK, dialog_rect, 3)
            
            # Title
            font_title = pygame.font.Font(None, 36)
            title_text = font_title.render("Level Complete!", True, Colors.GREEN)
            title_rect = title_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 40))
            self._level_complete_surface.blit(title_text, title_rect)
            
            # Next level info
            font_text = pygame.font.Font(None, 24)
            next_level_info = self.level_complete_data.get('next_level_info', 'Next Level')
            info_text = font_text.render(f"Starting: {next_level_info}", True, Colors.BLUE)
            info_rect = info_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 80))
            self._level_complete_surface.blit(info_text, info_rect)
            
            # Continue button instruction
            continue_text = font_text.render("Press SPACE to continue", True, Colors.BLACK)
            continue_rect = continue_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 120))
            self._level_complete_surface.blit(continue_text, continue_rect)
            
            # Restart instruction
            restart_text = font_text.render("Press R to restart from Level 1", True, Colors.GRAY)
            restart_rect = restart_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 150))
            self._level_complete_surface.blit(restart_text, restart_rect)
        
        # Simply blit the cached surface - no flickering
        self.screen.blit(self._level_complete_surface, (0, 0))
    
    def draw_debug_info(self, debug_info: dict):
        """
        Draw debug information
        Useful for development và testing
        """
        if not debug_info:
            return
        
        font = pygame.font.Font(None, 20)
        y_offset = SCREEN_HEIGHT - 150
        
        for key, value in debug_info.items():
            text = f"{key}: {value}"
            text_surface = font.render(text, True, Colors.BLACK)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def capture_screenshot(self, filename: str):
        """Capture screenshot của current game state"""
        pygame.image.save(self.screen, filename)
    
    def get_tower_at_position(self, pos) -> Tower:
        """
        Helper method để tìm tower tại position
        """
        x, y = pos
        for tower in self.towers:
            if tower.contains_point(x, y):
                return tower
        return None
