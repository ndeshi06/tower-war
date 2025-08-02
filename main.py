"""
Main game application - entry point
Thể hiện MVC Pattern và các OOP principles
"""
import pygame
import sys
from src.controllers.game_controller import GameController
from src.controllers.menu_manager import MenuManager
from src.views.game_view import GameView
from src.views.level_select_view import LevelSelectView
from src.views.game_result_view import GameResultView
from src.views.intro_view import show_intro
from src.utils.transition import fade_in, fade_out
from src.models.base import Observer
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GameSettings, GameState, OwnerType

class TowerWarGame(Observer):
    def save_progression(self):
        """Lưu tiến trình game hiện tại"""
        from src.utils.progression_manager import ProgressionManager
        pm = ProgressionManager()
        data = {}
        data['current_level'] = self.current_level
        if self.controller:
            # Lưu trạng thái các tower
            data['towers'] = [
                {
                    'x': t.x,
                    'y': t.y,
                    'owner': t.owner,
                    'troops': t.troops
                } for t in getattr(self.controller, 'towers', [])
            ]
            # Lưu trạng thái các troop
            data['troops'] = [
                {
                    'x': tr.x,
                    'y': tr.y,
                    'owner': tr.owner,
                    'count': getattr(tr, 'count', 1),
                    'target_position': getattr(tr, 'target_position', (0,0)),
                    'is_dead': getattr(tr, 'is_dead', False)
                } for tr in getattr(self.controller, 'troops', [])
            ]
        pm.save(data)
    """
    Main game application class
    Thể hiện Facade Pattern - cung cấp interface đơn giản cho complex subsystem
    """
    
    def __init__(self, screen=None):
        # Initialize pygame
        pygame.init()
        
        # Setup display - use existing screen if provided, otherwise create new one
        if screen is not None:
            self.screen = screen
            # Detect if we're in fullscreen mode by checking display flags
            current_size = screen.get_size()
            display_flags = pygame.display.get_surface().get_flags()
            self.fullscreen = bool(display_flags & pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen = False
            
        pygame.display.set_caption("Tower War")
        
        # Scaling for fullscreen mode
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Game loop components
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Views
        self.menu_manager = MenuManager(self.screen, self.clock)
        self.level_select_view = LevelSelectView(self.screen)
        self.game_result_view = GameResultView(self.screen)
        
        # Game components (MVC Pattern) - lazy initialization
        self.controller = None
        self.view = None
        
        # Game state management
        self.app_state = "menu"  # "menu", "level_select", "game", "result"
        self.current_level = 1
        self.winner = None
        self.has_next_level = True
        self.result_shown = False  # Flag để tránh hiển thị result nhiều lần
        
        # Input handling
        self.keys_pressed = set()

        # Music
        from src.utils.sound_manager import SoundManager
        self.sound_manager = SoundManager()
        self.sound_manager.preload()

    def start_game(self, level=1):
        """Khởi tạo game components với level cụ thể"""
        if not self.controller:
            # Tạo game components khi cần (Lazy initialization)
            self.controller = GameController()  
            self.view = GameView(self.screen)   
            
            # Setup Observer relationships
            self.controller.attach(self.view)
            self.controller.attach(self)  # Listen for game events
            
            # Update level select view với level manager reference
            self.level_select_view.level_manager = self.controller.level_manager
        
        # Set level và restart game
        if self.controller:
            self.controller.level_manager.set_level(level)
            self.controller.restart_game()
            self.current_level = level
            self.result_shown = False  # Reset flag
        
        # Switch from background music to gameview music
        self.sound_manager.play_gameview_music()
        
        self.app_state = "game"
        fade_in(self.screen, self.clock)
    
    def start_next_level(self):
        """Bắt đầu level tiếp theo"""
        if self.controller and self.controller.level_manager.advance_to_next_level():
            next_level = self.controller.level_manager.current_level
            self.controller.restart_game()
            self.current_level = next_level
            self.result_shown = False  # Reset flag
            
            # Continue with gameview music for next level
            self.sound_manager.play_gameview_music()
            
            self.app_state = "game"
            fade_in(self.screen, self.clock)
        else:
            self.return_to_menu()
    
    def show_level_select(self):
        """Hiển thị level selection"""
        # Đảm bảo controller và level manager đã được khởi tạo
        if not self.controller:
            # Initialize controller without starting gameview music
            self.controller = GameController()  
            self.view = GameView(self.screen)   
            
            # Setup Observer relationships
            self.controller.attach(self.view)
            self.controller.attach(self)  # Listen for game events
            
            # Initialize with level 1
            self.controller.level_manager.set_level(1)
            self.current_level = 1
        
        # Cập nhật level manager reference cho level select view
        self.level_select_view.level_manager = self.controller.level_manager
        
        # Don't restart music if already playing background music
        if not (self.sound_manager.is_music_playing() and 
                self.sound_manager.get_current_music_file() == "background_music.mp3"):
            self.sound_manager.play_background_music()
        
        self.app_state = "level_select"
        fade_in(self.screen, self.clock)
    
    def show_result(self, winner, level, has_next_level):
        """Hiển thị kết quả game"""
        if self.result_shown:  # Tránh hiển thị nhiều lần
            return
            
        self.app_state = "result"
        self.winner = winner
        self.current_level = level
        self.has_next_level = has_next_level
        self.result_shown = True
        self.game_result_view.reset_animation()
    
    def return_to_menu(self):
        """Quay về menu"""
        self.app_state = "menu"
        self.result_shown = False  # Reset flag
        self.menu_manager.reset_to_main()
        
        # Switch back to background music when returning to menu
        self.sound_manager.play_background_music()
        
        fade_in(self.screen, self.clock)
    
    def update_observer(self, event_type: str, data: dict):
        """Observer implementation để nhận events từ game controller"""
        if self.result_shown:  # Nếu đã hiển thị result rồi thì bỏ qua
            return
            
        if event_type == "level_complete":
            winner = data.get('winner')
            level = data.get('level', self.current_level)
            has_next = data.get('has_next_level', False)
            self.show_result(winner, level, has_next)
        
        elif event_type == "game_over":
            winner = data.get('winner')
            if winner != OwnerType.PLAYER:  # Player lost
                self.show_result(winner, self.current_level, False)
    
    def run(self):
        """
        Main game loop
        Template Method Pattern - định nghĩa skeleton của game loop
        """
        # Start appropriate music based on initial state
        if self.app_state == "menu":
            if (not self.sound_manager.is_music_playing() or 
                self.sound_manager.get_current_music_file() != "background_music.mp3"):
                self.sound_manager.play_background_music()
        
        try:
            while self.running:
                try:
                    # Calculate delta time
                    dt = self.clock.tick(GameSettings.FPS) / 1000.0
                    # Handle events
                    self._handle_events()
                    # Update game logic
                    self._update(dt)
                    # Render
                    self._render(dt)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.running = False
        finally:
            self.save_progression()
            self._cleanup()
    
    def _handle_events(self):
        """
        Handle all pygame events based on app state
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_progression()
                self.running = False
            # Handle F11 globally across all states
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            
            # Pass events directly without scaling
            scaled_event = event
            if self.app_state == "menu":
                action = self.menu_manager.handle_event(scaled_event)
                if action == "start_game":
                    fade_out(self.screen, self.clock)
                    self.show_level_select()
                elif action == "continue_game":
                    fade_out(self.screen, self.clock)
                    self.load_progression()
                elif action == "new_game":
                    fade_out(self.screen, self.clock)
                    self.reset_progression()
                    self.show_level_select()
                elif action == "quit":
                    fade_out(self.screen, self.clock)
                    self.running = False
            elif self.app_state == "level_select":
                # Level selection events
                action = self.level_select_view.handle_event(scaled_event)
                if action and action.startswith("level_"):
                    level = int(action.split("_")[1])
                    fade_out(self.screen, self.clock)
                    self.start_game(level)
                elif action == "back_to_menu":
                    fade_out(self.screen, self.clock)
                    self.return_to_menu()
            elif self.app_state == "result":
                # Game result events
                action = self.game_result_view.handle_event(scaled_event)
                if action == "next_level":
                    fade_out(self.screen, self.clock)
                    self.start_next_level()
                elif action == "play_again":
                    self.result_shown = False  # Reset flag
                    fade_out(self.screen, self.clock)
                    self.start_game(self.current_level)
                elif action == "main_menu":
                    fade_out(self.screen, self.clock)
                    self.return_to_menu()
            elif self.app_state == "game":
                # Game events
                if scaled_event.type == pygame.KEYDOWN:
                    self._handle_keydown(scaled_event)
                elif scaled_event.type == pygame.KEYUP:
                    self._handle_keyup(scaled_event)
                elif scaled_event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(scaled_event)
                elif scaled_event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(scaled_event)

    def load_progression(self):
        """Tải tiến trình đã lưu và chuyển sang màn hình chọn level, highlight level đã lưu"""
        from src.utils.progression_manager import ProgressionManager
        pm = ProgressionManager()
        data = pm.load()
        if not data:
            return
        # Lưu lại level đã lưu để highlight trong màn hình chọn level
        self.current_level = data.get('current_level', 1)
        self.show_level_select()

    def reset_progression(self):
        """Xóa file progression để bắt đầu game mới"""
        from src.utils.progression_manager import ProgressionManager
        import os
        pm = ProgressionManager()
        if os.path.exists(pm.save_path):
            os.remove(pm.save_path)
    
    def _handle_keydown(self, event):
        """Handle key press events"""
        self.keys_pressed.add(event.key)
        
        # Game controls (only if game is active)
        if not self.controller:
            return
        
        # ESC to pause/unpause game (not return to menu)
        if event.key == pygame.K_ESCAPE:
            if self.controller.game_state == GameState.PLAYING:
                self.controller.pause_game()
                if self.view:
                    # Sync current sound settings to pause menu
                    self._sync_sound_settings_to_pause_menu()
                    self.view.show_pause_menu()
            elif self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                if self.view:
                    self.view.hide_pause_menu()
            return
        
        # Handle level complete inputs
        elif self.controller.game_state == GameState.LEVEL_COMPLETE:
            self.controller.handle_level_complete_input(event.key)
        
        # SPACE for alternative pause/unpause
        elif event.key == pygame.K_SPACE:
            if self.controller.game_state == GameState.PLAYING:
                self.controller.pause_game()
                if self.view:
                    # Sync current sound settings to pause menu
                    self._sync_sound_settings_to_pause_menu()
                    self.view.show_pause_menu()
            elif self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                if self.view:
                    self.view.hide_pause_menu()
    
    def _sync_sound_settings_to_pause_menu(self):
        """Sync current sound settings to pause menu"""
        if self.view and self.view.pause_menu:
            # Get current settings from menu manager
            self.view.pause_menu.sound_enabled = self.menu_manager.is_sound_enabled()
            self.view.pause_menu.music_enabled = self.menu_manager.is_music_enabled()
    
    def _handle_keyup(self, event):
        """Handle key release events"""
        if event.key in self.keys_pressed:
            self.keys_pressed.remove(event.key)
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events"""
        if event.button == 1:  # Left click
            if self.controller and self.view:
                # Translate mouse coordinates for UI clicks
                scale_factor = self.view.scale_factor
                offset_x = getattr(self.view, 'offset_x', 0)
                offset_y = getattr(self.view, 'offset_y', 0)
                
                # Translate mouse coordinates from screen to game coordinates
                mouse_x = event.pos[0] - offset_x
                mouse_y = event.pos[1] - offset_y
                translated_x = mouse_x / scale_factor
                translated_y = mouse_y / scale_factor
                
                # Use translated coordinates for UI if within game area
                if (0 <= translated_x <= SCREEN_WIDTH and 0 <= translated_y <= SCREEN_HEIGHT):
                    ui_pos = (translated_x, translated_y)
                else:
                    ui_pos = event.pos
                
                # Check UI clicks first
                ui_action = self.view.handle_ui_click(ui_pos)
                
                if ui_action == "restart":
                    # Hide pause menu first
                    if self.view:
                        self.view.hide_pause_menu()
                    self.result_shown = False  # Reset flag
                    self.controller.restart_game()
                    # Ensure gameview music is playing
                    self.sound_manager.play_gameview_music()
                elif ui_action == "resume":
                    if hasattr(self.controller, 'pause_game'):
                        self.controller.pause_game()  # This will unpause
                elif ui_action == "menu":
                    fade_out(self.screen, self.clock)
                    self.return_to_menu()
                elif ui_action == "toggle_sound":
                    # Toggle sound effects in pause menu
                    if self.view and hasattr(self.view, 'pause_menu'):
                        self.view.pause_menu.sound_enabled = not self.view.pause_menu.sound_enabled
                        # Update sound manager (use the instance)
                        if self.view.pause_menu.sound_enabled:
                            self.sound_manager.set_sfx_volume(0.7)
                        else:
                            self.sound_manager.set_sfx_volume(0.0)
                        # Sync back to menu manager
                        self.menu_manager.settings_menu.sound_enabled = self.view.pause_menu.sound_enabled
                elif ui_action == "toggle_music":
                    # Toggle background music in pause menu
                    if self.view and hasattr(self.view, 'pause_menu'):
                        self.view.pause_menu.music_enabled = not self.view.pause_menu.music_enabled
                        # Update sound manager (use the instance)
                        if self.view.pause_menu.music_enabled:
                            self.sound_manager.set_music_volume(0.5)
                        else:
                            self.sound_manager.set_music_volume(0.0)
                        # Sync back to menu manager
                        self.menu_manager.settings_menu.music_enabled = self.view.pause_menu.music_enabled
                else:
                    # Game click - only if not paused
                    if self.controller.game_state == GameState.PLAYING:
                        # Use the same translated coordinates from UI click handling
                        if (0 <= translated_x <= SCREEN_WIDTH and 0 <= translated_y <= SCREEN_HEIGHT):
                            self.controller.handle_click((translated_x, translated_y))
                        else:
                            # Fallback to original coordinates if translation failed
                            self.controller.handle_click(event.pos)
    
    def _handle_mouse_motion(self, event):
        """Handle mouse motion events"""
        if self.view:
            # Translate mouse coordinates for UI elements in fullscreen mode
            scale_factor = self.view.scale_factor
            offset_x = getattr(self.view, 'offset_x', 0)
            offset_y = getattr(self.view, 'offset_y', 0)
            
            # Translate mouse coordinates from screen to game coordinates
            mouse_x = event.pos[0] - offset_x
            mouse_y = event.pos[1] - offset_y
            translated_x = mouse_x / scale_factor
            translated_y = mouse_y / scale_factor
            
            # Only update if within game area, otherwise use original coordinates
            if (0 <= translated_x <= SCREEN_WIDTH and 0 <= translated_y <= SCREEN_HEIGHT):
                self.view.update_mouse_position((translated_x, translated_y))
            else:
                self.view.update_mouse_position(event.pos)
    
    def _update(self, dt):
        """
        Update game state based on app state
        """
        if self.app_state == "menu":
            self.menu_manager.update(dt)
            
        elif self.app_state == "level_select":
            self.level_select_view.update(dt)
            
        elif self.app_state == "game":
            if self.controller:
                # Chỉ update game nếu không ở trạng thái level complete
                if self.controller.game_state != GameState.LEVEL_COMPLETE:
                    self.controller.update(dt)
                
        elif self.app_state == "result":
            self.game_result_view.update(dt)
    
    def _render(self, dt):
        """
        Render current frame based on app state
        """
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        if self.app_state == "menu":
            # Render menu
            self.menu_manager.render(self.screen)
            
        elif self.app_state == "level_select":
            # Render level selection
            self.level_select_view.draw(self.screen)
            
        elif self.app_state == "game":
            # Render game
            if self.view:
                self.view.draw(dt)
                    
        elif self.app_state == "result":
            # Render game result - don't draw game view to prevent flickering
            # Clear screen with black background
            self.screen.fill((0, 0, 0))
            
            # Draw result overlay only
            if self.winner == OwnerType.PLAYER:
                all_complete = self.current_level >= 3 and not self.has_next_level
                self.game_result_view.draw_win_screen(
                    self.screen, self.current_level, self.has_next_level, all_complete
                )
            else:
                self.game_result_view.draw_lose_screen(self.screen, self.current_level)
        
        # Update display
        pygame.display.flip()
    
    def _cleanup(self):
        """Clean up resources"""
        pygame.quit()
        sys.exit()
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        # Reset display to avoid issues
        pygame.display.quit()
        pygame.display.init()
        
        if self.fullscreen:
            # Native fullscreen resolution
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Windowed mode with original resolution
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Tower War")
        
        # Reset scaling values (no longer needed)
        self.scale_x = 1.0
        self.scale_y = 1.0  
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Update views with new screen
        if self.view:
            self.view.screen = self.screen
        
        # Update all other views with new screen
        self.menu_manager.screen = self.screen
        self.level_select_view.screen = self.screen
        self.game_result_view.screen = self.screen


def main():
    """Entry point"""
        
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower War")

        from src.views.intro_view import show_intro
        screen = show_intro(screen, max_duration=4000)  # Loading tối đa 4 giây, get updated screen

        game = TowerWarGame(screen)  # Pass the screen from intro
        # Don't start music here - let the game decide based on state
        game.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
