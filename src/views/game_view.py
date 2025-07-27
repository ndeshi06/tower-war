"""
Game View - Main rendering class
Thể hiện MVC Pattern và Observer Pattern
"""
import pygame
import os
from typing import List
from ..models.base import Observer
from ..models.tower import Tower
from ..models.troop import Troop
from ..views.ui_view import GameHUD, GameOverScreen, PauseMenu
from ..utils.constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, GameState, GameSettings

class GameView(Observer):
    class DeadTroopAnim:
        def __init__(self, x, y, owner, size, start_time, animation_manager):
            self.x = x
            self.y = y
            self.owner = owner
            self.size = size
            self.start_time = start_time
            self.animation_manager = animation_manager
        def draw(self, screen, now):
            if self.owner == 'player':
                frames = self.animation_manager.get_player_troops_dead(self.size)
            else:
                frames = self.animation_manager.get_enemy_troops_dead(self.size)
            frame_count = len(frames)
            frame_idx = int((now - self.start_time) / 100) % frame_count
            frame = frames[frame_idx]
            rect = frame.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(frame, rect)
    """
    Main game view class - responsible for rendering all game objects
    Thể hiện Observer Pattern - quan sát game state changes
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background_color = Colors.WHITE
        
        # Load background image
        from ..utils.image_manager import ImageManager
        from ..utils.animation_manager import AnimationManager
        self.image_manager = ImageManager()
        self.animation_manager = AnimationManager(os.path.join(os.path.dirname(__file__), '..', '..', 'animations'))
        self.background_image = self.image_manager.get_image("background_game")
        
        # Scaling factor for consistent rendering
        self.scale_factor = 1.0
        
        # UI Components
        self.hud = GameHUD()
        self.game_over_screen = GameOverScreen()
        self.pause_menu = PauseMenu()
        
        # Game state
        self.game_state = GameState.PLAYING
        self.towers: List[Tower] = []
        self.troops: List[Troop] = []
        self.dead_animations = []
        
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
            # Cách đơn giản và chắc chắn: mỗi lần troop bị remove và là dead thì tạo anim mới
            old_troops = getattr(self, '_last_troops', [])
            new_troops = data.get('troops', [])
            self.troops = new_troops
            now = pygame.time.get_ticks()
            # Xoá dead animation đã hết thời gian
            def anim_duration(anim):
                if anim.owner == 'player':
                    frames = anim.animation_manager.get_player_troops_dead(anim.size)
                else:
                    frames = anim.animation_manager.get_enemy_troops_dead(anim.size)
                if not frames or len(frames) == 0:
                    return 500
                return len(frames) * 100
            self.dead_animations[:] = [anim for anim in self.dead_animations if now - anim.start_time < anim_duration(anim)]
            # Tạo anim cho troop vừa bị remove và là dead
            old_dead = [t for t in old_troops if getattr(t, 'is_dead', False) and getattr(t, 'dead_time', None) is not None]
            new_ids = set(id(t) for t in new_troops)
            for troop in old_dead:
                if id(troop) not in new_ids:
                    size = (max(1, int(troop.radius * 2 * self.scale_factor)),) * 2
                    # Sử dụng troop.dead_time làm start_time để đảm bảo anim hết hạn đúng lúc
                    start_time = getattr(troop, 'dead_time', now)
                    anim = self.DeadTroopAnim(troop.x * self.scale_factor, troop.y * self.scale_factor, troop.owner, size, start_time, self.animation_manager)
                    self.dead_animations.append(anim)
            self._last_troops = list(new_troops)
        
        elif event_type == "game_over":
            self.game_state = GameState.GAME_OVER  
            self.game_over_screen.update_observer(event_type, data)
            # Reset level complete dialog
            self.show_level_complete_dialog = False
            self.level_complete_data = None
            print(f"GameView: Game over! Winner: {data.get('winner')}")
        
        elif event_type == "level_complete":
            self.game_state = GameState.LEVEL_COMPLETE
            # Don't show our own dialog - let main.py handle it
            self.show_level_complete_dialog = False
            self.level_complete_data = None
            self._level_complete_surface = None
            print(f"GameView: Level complete! Letting main.py handle dialog")
        
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
        # Calculate current scale factor for consistent rendering
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale_x = screen_width / SCREEN_WIDTH
        scale_y = screen_height / SCREEN_HEIGHT
        self.scale_factor = min(scale_x, scale_y)  # Use uniform scaling to maintain aspect ratio
        
        # Update UI components with current screen
        # Update UI components screen references
        if hasattr(self.hud, 'screen'):
            self.hud.screen = self.screen
        if hasattr(self.game_over_screen, 'screen'):
            self.game_over_screen.screen = self.screen
        if hasattr(self.pause_menu, 'screen'):
            self.pause_menu.screen = self.screen
            
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
            # Scale background to fit current screen size
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            scaled_bg = pygame.transform.scale(self.background_image, (screen_width, screen_height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            self.screen.fill(self.background_color)
    
    def _draw_background(self):
        """Draw background elements như grid"""
        if self.show_grid:
            self._draw_grid()
    
    def _draw_grid(self):
        """Draw grid để debug hoặc visual aid"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        grid_size = 50
        grid_color = (230, 230, 230)
        
        # Vertical lines
        for x in range(0, screen_width, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, screen_height))
        
        # Horizontal lines
        for y in range(0, screen_height, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (screen_width, y))
    
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
        """Draw all towers with proper scaling"""
        for tower in self.towers:
            if tower.active:
                self._draw_scaled_tower(tower)
                # Đã tắt hiệu ứng selection mờ khi chọn tower
    
    def _draw_scaled_tower(self, tower: Tower):
        """Draw a single tower with scaling, including flying rock effect"""
        # Tạm thời scale lại surface để vẽ tower đúng vị trí và hiệu ứng
        # Tạo surface tạm để vẽ tower ở scale 1.0, sau đó scale/blit lên màn hình chính
        # Nhưng để đơn giản, ta sẽ vẽ trực tiếp lên màn hình với scale hiện tại
        # Lưu lại các thuộc tính gốc
        orig_x, orig_y = tower.x, tower.y
        orig_radius = tower.radius
        orig_scale = getattr(tower, '_scale', 1.0)
        # Scale các thuộc tính
        tower.x = tower.x * self.scale_factor
        tower.y = tower.y * self.scale_factor
        tower._scale = tower._scale * self.scale_factor
        # Vẽ tower (bao gồm flying rock)
        tower.draw(self.screen)
        # Vẽ selection highlight nếu cần
        if tower.selected:
            pygame.draw.circle(self.screen, Colors.WHITE, (int(tower.x), int(tower.y)), int(tower.radius * tower._scale) + 5, 3)
        # Vẽ số quân với scale phù hợp (nếu cần override)
        # Khôi phục thuộc tính gốc
        tower.x = orig_x
        tower.y = orig_y
        tower._scale = orig_scale
    
    def _draw_scaled_troops_text(self, tower: Tower, x: int, y: int, radius: int):
        """Draw troops text with proper scaling"""
        try:
            font_size = int(GameSettings.FONT_MEDIUM * self.scale_factor)
            font = pygame.font.SysFont('Arial', font_size, bold=True)
        except:
            font_size = int(24 * self.scale_factor)  # Fallback size
            font = pygame.font.Font(None, font_size)
        
        # Render text
        text = font.render(str(tower.troops), True, Colors.WHITE)
        text_rect = text.get_rect(midbottom=(x, y - radius - int(4 * self.scale_factor)))
        
        # Draw shadow for better visibility
        shadow = font.render(str(tower.troops), True, Colors.BLACK)
        shadow_rect = shadow.get_rect(midbottom=(x + 1, y - radius - int(3 * self.scale_factor)))
        
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text, text_rect)
    
    def _draw_selection_effect(self, tower: Tower):
        """
        Draw selection effect cho selected tower with proper scaling
        Animated pulse effect
        """
        import math
        
        # Calculate scaled position and radius
        scaled_x = int(tower.x * self.scale_factor)
        scaled_y = int(tower.y * self.scale_factor)
        scaled_radius = int(tower.radius * self.scale_factor)
        
        # Pulse effect
        pulse_factor = (math.sin(self.selection_pulse_time * 5) + 1) / 2  # 0-1
        pulse_radius = scaled_radius + int(5 * self.scale_factor) + int(pulse_factor * 10 * self.scale_factor)
        
        # Draw pulsing circle
        alpha = int(100 + (pulse_factor * 100))  # 100-200
        
        # Create surface with alpha
        surface_size = int(pulse_radius * 4)
        pulse_surface = pygame.Surface((surface_size, surface_size))
        pulse_surface.set_alpha(alpha)
        pulse_surface.fill(Colors.WHITE)
        
        pygame.draw.circle(pulse_surface, Colors.BLUE, 
                         (surface_size // 2, surface_size // 2), 
                         pulse_radius, max(1, int(3 * self.scale_factor)))
        
        # Blit pulse surface
        pulse_rect = pulse_surface.get_rect(center=(scaled_x, scaled_y))
        self.screen.blit(pulse_surface, pulse_rect)
    
    def _draw_troops(self):
        """Draw all troops with proper scaling - simplified without paths"""
        now = pygame.time.get_ticks()
        # Luôn xoá dead animation đã hết thời gian ở đây (dù không có update_observer)
        def anim_duration(anim):
            if anim.owner == 'player':
                frames = anim.animation_manager.get_player_troops_dead(anim.size)
            else:
                frames = anim.animation_manager.get_enemy_troops_dead(anim.size)
            # Nếu frames rỗng, fallback 500ms để không bị giữ vĩnh viễn
            if not frames or len(frames) == 0:
                return 500
            return len(frames) * 100  # mỗi frame 100ms, giống draw()

        # Vẽ troop sống bình thường trước
        for troop in self.troops:
            if troop.active:
                self._draw_scaled_troop(troop)
        # Sau đó vẽ dead animation lên trên cùng
        self.dead_animations[:] = [anim for anim in self.dead_animations if now - anim.start_time < anim_duration(anim)]
        for anim in self.dead_animations:
            anim.draw(self.screen, now)
    
    def _draw_scaled_troop(self, troop: Troop):
        """Draw a single troop with animation (cat/dog), dog sẽ flip nếu chạy sang trái"""
        scaled_x = int(troop.x * self.scale_factor)
        scaled_y = int(troop.y * self.scale_factor)
        size = (max(1, int(troop.radius * 2 * self.scale_factor)),) * 2
        now = pygame.time.get_ticks()
        if hasattr(troop, 'is_dead') and troop.is_dead:
            dead_time = getattr(troop, 'dead_time', None)
            base_time = dead_time if dead_time is not None else now
            elapsed = now - base_time
            dust_size = tuple(int(s * 2) for s in size)
            dust_frames = list(self.animation_manager.get_attack_animation(dust_size))
            dust_frame_count = 9
            dust_total = dust_frame_count * 100
            if troop.owner == 'player':
                dead_frames = list(self.animation_manager.get_player_troops_dead(size))
            else:
                dead_frames = list(self.animation_manager.get_enemy_troops_dead(size))
            dead_frame_count = len(dead_frames)
            # Nếu chưa hết dust thì chỉ vẽ dust
            if elapsed < dust_total:
                frame_idx = int(elapsed // 100)
                if frame_idx >= dust_frame_count:
                    frame_idx = dust_frame_count - 1
                frame = dust_frames[frame_idx]
            else:
                dead_elapsed = elapsed - dust_total
                if dead_frame_count == 0:
                    return
                frame_idx = int(dead_elapsed // 100) % dead_frame_count
                frame = dead_frames[frame_idx]
        else:
            if troop.owner == 'player':
                frames = list(self.animation_manager.get_player_troops_run(size))
            else:
                frames = list(self.animation_manager.get_enemy_troops_run(size))
            if not frames:
                return
            frame_count = len(frames)
            frame_idx = int(now / 100) % frame_count
            frame = frames[frame_idx]
        # Flip dog nếu di chuyển sang trái
        if troop.owner == 'enemy' and hasattr(troop, 'x') and hasattr(troop, 'target_position'):
            target_x, _ = troop.target_position
            if target_x < troop.x:
                frame = pygame.transform.flip(frame, True, False)
        rect = frame.get_rect(center=(scaled_x, scaled_y))
        self.screen.blit(frame, rect)
    
    def _draw_troop_direction_arrow(self, troop: Troop, scaled_x: int, scaled_y: int, scaled_radius: int):
        """Draw direction arrow on troop"""
        import math
        
        target_x, target_y = troop.target_position
        
        # Calculate direction vector
        dx = target_x - troop.x
        dy = target_y - troop.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction
            norm_dx = dx / distance
            norm_dy = dy / distance
            
            # Arrow parameters
            arrow_length = scaled_radius * 0.8
            arrow_head_size = scaled_radius * 0.4
            
            # Arrow end point (inside the troop circle)
            arrow_end_x = scaled_x + norm_dx * arrow_length
            arrow_end_y = scaled_y + norm_dy * arrow_length
            
            # Arrow start point
            arrow_start_x = scaled_x - norm_dx * arrow_length * 0.3
            arrow_start_y = scaled_y - norm_dy * arrow_length * 0.3
            
            # Draw arrow shaft
            pygame.draw.line(self.screen, Colors.WHITE, 
                           (arrow_start_x, arrow_start_y), 
                           (arrow_end_x, arrow_end_y), 
                           max(1, int(2 * self.scale_factor)))
            
            # Draw arrow head
            head_angle = math.atan2(norm_dy, norm_dx)
            head_angle1 = head_angle + 2.5  # 143 degrees
            head_angle2 = head_angle - 2.5  # 143 degrees
            
            head_x1 = arrow_end_x - arrow_head_size * math.cos(head_angle1)
            head_y1 = arrow_end_y - arrow_head_size * math.sin(head_angle1)
            head_x2 = arrow_end_x - arrow_head_size * math.cos(head_angle2)
            head_y2 = arrow_end_y - arrow_head_size * math.sin(head_angle2)
            
            # Draw arrow head lines
            pygame.draw.line(self.screen, Colors.WHITE, 
                           (arrow_end_x, arrow_end_y), (head_x1, head_y1), 
                           max(1, int(2 * self.scale_factor)))
            pygame.draw.line(self.screen, Colors.WHITE, 
                           (arrow_end_x, arrow_end_y), (head_x2, head_y2), 
                           max(1, int(2 * self.scale_factor)))
    
    def _draw_troop_path(self, troop: Troop, scaled_x: int, scaled_y: int):
        """Draw path line from troops to their actual targets - không vẽ quá xa"""
        import math
        
        target_x, target_y = troop.target_position
        
        # Kiểm tra khoảng cách - nếu quá xa thì không vẽ đường
        distance_to_target = math.sqrt((target_x - troop.x)**2 + (target_y - troop.y)**2)
        if distance_to_target > 300:  # Giới hạn khoảng cách vẽ đường
            return
        
        # Scale target position
        scaled_target_x = int(target_x * self.scale_factor)
        scaled_target_y = int(target_y * self.scale_factor)
        
        # Path color based on troop owner
        path_color = troop.get_color()
        # Make path color more transparent and thinner
        alpha_color = tuple(c // 4 for c in path_color)  # Làm mờ hơn
        
        # Only draw path if target is reasonable
        self._draw_dashed_line(self.screen, alpha_color,
                             (scaled_x, scaled_y),
                             (scaled_target_x, scaled_target_y), 
                             max(1, int(1 * self.scale_factor)), 
                             max(8, int(15 * self.scale_factor)))  # Dash dài hơn

    def _draw_tower_connections(self):
        """
        Draw connections từ selected tower đến các towers khác with proper scaling
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
                
                # Scale positions for connections
                start_x = int(selected_tower.x * self.scale_factor)
                start_y = int(selected_tower.y * self.scale_factor)
                end_x = int(tower.x * self.scale_factor)
                end_y = int(tower.y * self.scale_factor)
                scaled_width = max(1, int(2 * self.scale_factor))
                scaled_dash = max(2, int(10 * self.scale_factor))
                
                # Draw dashed line with scaling
                self._draw_dashed_line(self.screen, line_color,
                                     (start_x, start_y),
                                     (end_x, end_y), scaled_width, scaled_dash)
    
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
        
        # Priority order: Pause menu > Game over (no level complete dialog here)
        if self.game_state == GameState.PAUSED:
            # Draw pause menu if paused (highest priority)
            self.pause_menu.draw(self.screen)
        elif self.game_state == GameState.GAME_OVER:
            # Draw game over screen only for actual game over (not level complete)
            self.game_over_screen.draw(self.screen)
        # Note: Level complete dialog is handled by main.py's result state
    
    def _draw_level_complete_dialog(self):
        """Vẽ dialog khi hoàn thành level"""
        # Create dialog surface only once to prevent flickering
        if self._level_complete_surface is None:
            # Get current screen dimensions
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # Create a surface for the entire dialog
            self._level_complete_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% alpha
            self._level_complete_surface.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 400
            dialog_height = 200
            dialog_x = (screen_width - dialog_width) // 2
            dialog_y = (screen_height - dialog_height) // 2
            
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
