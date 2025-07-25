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
from src.models.base import Observer
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GameSettings, GameState, OwnerType

class TowerWarGame(Observer):
    """
    Main game application class
    Thể hiện Facade Pattern - cung cấp interface đơn giản cho complex subsystem
    """
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower War")
        self.fullscreen = False
        
        # Scaling for fullscreen mode
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Views
        self.menu_manager = MenuManager(self.screen)
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
        
        # Game loop components
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = False
        
        # Input handling
        self.keys_pressed = set()

        # Music
        from src.utils.sound_manager import SoundManager
        sound_manager = SoundManager()
        sound_manager.preload()
        print(">>> Playing background music")
        sound_manager.play_background_music()

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
        
        self.app_state = "game"
        print(f"Game started at level {level}")
    
    def start_next_level(self):
        """Bắt đầu level tiếp theo"""
        if self.controller and self.controller.level_manager.advance_to_next_level():
            next_level = self.controller.level_manager.current_level
            self.controller.restart_game()
            self.current_level = next_level
            self.result_shown = False  # Reset flag
            self.app_state = "game"
            print(f"Advanced to level {next_level}")
        else:
            print("No more levels available")
            self.return_to_menu()
    
    def show_level_select(self):
        """Hiển thị level selection"""
        # Đảm bảo controller và level manager đã được khởi tạo
        if not self.controller:
            self.start_game(1)  # Khởi tạo controller với level 1
            self.return_to_menu()  # Quay về menu sau khi khởi tạo
        
        # Cập nhật level manager reference cho level select view
        self.level_select_view.level_manager = self.controller.level_manager
        
        self.app_state = "level_select"
        print("Showing level selection")
    
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
        print(f"Showing result: Winner={winner}, Level={level}, HasNext={has_next_level}")
    
    def return_to_menu(self):
        """Quay về menu"""
        self.app_state = "menu"
        self.result_shown = False  # Reset flag
        self.menu_manager.reset_to_main()
        print("Returned to main menu")
    
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
        print("Starting Tower War Game...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(GameSettings.FPS) / 1000.0
            
            # Handle events
            self._handle_events()
            
            # Update game logic
            self._update(dt)
            
            # Render
            self._render(dt)
        
        self._cleanup()
    
    def _handle_events(self):
        """
        Handle all pygame events based on app state
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle F11 globally across all states
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            
            # Scale mouse events if in fullscreen
            scaled_event = event
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                if self.fullscreen and self.scale != 1.0:
                    mouse_x, mouse_y = event.pos
                    # Convert screen coordinates to game coordinates
                    mouse_x = (mouse_x - self.offset_x) / self.scale
                    mouse_y = (mouse_y - self.offset_y) / self.scale
                    # Clamp to game area
                    mouse_x = max(0, min(SCREEN_WIDTH, mouse_x))
                    mouse_y = max(0, min(SCREEN_HEIGHT, mouse_y))
                    
                    # Create new event with scaled coordinates
                    scaled_event = pygame.event.Event(event.type, event.dict)
                    scaled_event.pos = (int(mouse_x), int(mouse_y))
            
            if self.app_state == "menu":
                # Menu events
                action = self.menu_manager.handle_event(scaled_event)
                if action == "start_game":
                    self.show_level_select()
                elif action == "quit":
                    self.running = False
                    
            elif self.app_state == "level_select":
                # Level selection events
                action = self.level_select_view.handle_event(scaled_event)
                if action and action.startswith("level_"):
                    level = int(action.split("_")[1])
                    self.start_game(level)
                elif action == "back_to_menu":
                    self.return_to_menu()
                    
            elif self.app_state == "result":
                # Game result events
                action = self.game_result_view.handle_event(scaled_event)
                if action == "next_level":
                    self.start_next_level()
                elif action == "play_again":
                    self.result_shown = False  # Reset flag
                    self.start_game(self.current_level)
                elif action == "main_menu":
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
                # Check UI clicks first
                ui_action = self.view.handle_ui_click(event.pos)
                
                if ui_action == "restart":
                    # Hide pause menu first
                    if self.view:
                        self.view.hide_pause_menu()
                    self.result_shown = False  # Reset flag
                    self.controller.restart_game()
                    print("Game restarted")
                elif ui_action == "resume":
                    if hasattr(self.controller, 'pause_game'):
                        self.controller.pause_game()  # This will unpause
                        print("Game resumed")
                elif ui_action == "menu":
                    self.return_to_menu()
                    print("Returned to menu")
                elif ui_action == "toggle_sound":
                    # Toggle sound effects in pause menu
                    if self.view and hasattr(self.view, 'pause_menu'):
                        self.view.pause_menu.sound_enabled = not self.view.pause_menu.sound_enabled
                        # Update sound manager
                        from src.utils.sound_manager import SoundManager
                        sound_manager = SoundManager()
                        if self.view.pause_menu.sound_enabled:
                            sound_manager.set_sfx_volume(0.7)
                        else:
                            sound_manager.set_sfx_volume(0.0)
                        print(f"Sound effects {'enabled' if self.view.pause_menu.sound_enabled else 'disabled'}")
                        # Sync back to menu manager
                        self.menu_manager.settings_menu.sound_enabled = self.view.pause_menu.sound_enabled
                elif ui_action == "toggle_music":
                    # Toggle background music in pause menu
                    if self.view and hasattr(self.view, 'pause_menu'):
                        self.view.pause_menu.music_enabled = not self.view.pause_menu.music_enabled
                        # Update sound manager
                        from src.utils.sound_manager import SoundManager
                        sound_manager = SoundManager()
                        if self.view.pause_menu.music_enabled:
                            sound_manager.set_music_volume(0.5)
                        else:
                            sound_manager.set_music_volume(0.0)
                        print(f"Background music {'enabled' if self.view.pause_menu.music_enabled else 'disabled'}")
                        # Sync back to menu manager
                        self.menu_manager.settings_menu.music_enabled = self.view.pause_menu.music_enabled
                else:
                    # Game click - only if not paused
                    if self.controller.game_state == GameState.PLAYING:
                        self.controller.handle_click(event.pos)
    
    def _handle_mouse_motion(self, event):
        """Handle mouse motion events"""
        if self.view:
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
        
        # Create a surface for the game content
        if self.fullscreen and self.scale != 1.0:
            # Create a surface with original game size
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill((0, 0, 0))
            current_surface = game_surface
        else:
            current_surface = self.screen
        
        if self.app_state == "menu":
            # Render menu
            self.menu_manager.render(current_surface)
            
        elif self.app_state == "level_select":
            # Render level selection
            self.level_select_view.draw(current_surface)
            
        elif self.app_state == "game":
            # Render game
            if self.view:
                # Temporarily update view's screen reference for fullscreen
                original_screen = self.view.screen
                self.view.screen = current_surface
                self.view.draw(dt)
                self.view.screen = original_screen  # Restore
                
                # Debug overlay
                if self.debug_mode:
                    self._render_debug_info(current_surface)
                    
        elif self.app_state == "result":
            # Render game result - don't draw game view to prevent flickering
            # Clear screen with black background
            current_surface.fill((0, 0, 0))
            
            # Draw result overlay only
            if self.winner == OwnerType.PLAYER:
                all_complete = self.current_level >= 3 and not self.has_next_level
                self.game_result_view.draw_win_screen(
                    current_surface, self.current_level, self.has_next_level, all_complete
                )
            else:
                self.game_result_view.draw_lose_screen(current_surface, self.current_level)
        
        # Scale and blit to actual screen if in fullscreen
        if self.fullscreen and self.scale != 1.0:
            # Scale the game surface maintaining aspect ratio
            scaled_width = int(SCREEN_WIDTH * self.scale)
            scaled_height = int(SCREEN_HEIGHT * self.scale)
            scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))
            self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self, surface=None):
        """Render debug information overlay"""
        if not self.controller:
            return
        
        if surface is None:
            surface = self.screen
            
        import pygame.font
        font = pygame.font.Font(None, 24)
        
        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Game State: {self.controller.game_state}",
            f"Player Towers: {len([t for t in self.controller.towers if t.owner == OwnerType.PLAYER])}",
            f"Enemy Towers: {len([t for t in self.controller.towers if t.owner == OwnerType.ENEMY])}",
            f"Neutral Towers: {len([t for t in self.controller.towers if t.owner == OwnerType.NEUTRAL])}",
            f"Active Troops: {len(self.controller.troops)}",
            f"Current Level: {self.current_level}"
        ]
        
        y_offset = 10
        for info in debug_info:
            text_surface = font.render(info, True, (255, 255, 0))
            surface.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def _cleanup(self):
        """Clean up resources"""
        print("Cleaning up game resources...")
        pygame.quit()
        sys.exit()
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Get current display info to scale properly
            info = pygame.display.Info()
            screen_width = info.current_w
            screen_height = info.current_h
            
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
            print(f"Switched to fullscreen mode ({screen_width}x{screen_height})")
            
            # Calculate scaling factors while keeping aspect ratio
            scale_x = screen_width / SCREEN_WIDTH
            scale_y = screen_height / SCREEN_HEIGHT
            # Use the smaller scale to maintain aspect ratio
            self.scale = min(scale_x, scale_y)
            self.scale_x = self.scale
            self.scale_y = self.scale
            
            # Calculate scaled dimensions and center the game
            scaled_width = int(SCREEN_WIDTH * self.scale)
            scaled_height = int(SCREEN_HEIGHT * self.scale)
            self.offset_x = (screen_width - scaled_width) // 2
            self.offset_y = (screen_height - scaled_height) // 2
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Switched to windowed mode")
            
            # Reset scaling
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
        game = TowerWarGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
