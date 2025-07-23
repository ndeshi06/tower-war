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
        
        # Views
        self.menu_manager = MenuManager()
        self.level_select_view = LevelSelectView()
        self.game_result_view = GameResultView()
        
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
    
    def start_game(self, level=1):
        """Khởi tạo game components với level cụ thể"""
        if not self.controller:
            # Tạo game components khi cần (Lazy initialization)
            self.controller = GameController()  
            self.view = GameView(self.screen)   
            
            # Setup Observer relationships
            self.controller.attach(self.view)
            self.controller.attach(self)  # Listen for game events
        
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
            
            if self.app_state == "menu":
                # Menu events
                action = self.menu_manager.handle_event(event)
                if action == "start_game":
                    self.show_level_select()
                elif action == "quit":
                    self.running = False
                    
            elif self.app_state == "level_select":
                # Level selection events
                action = self.level_select_view.handle_event(event)
                if action and action.startswith("level_"):
                    level = int(action.split("_")[1])
                    self.start_game(level)
                elif action == "back_to_menu":
                    self.return_to_menu()
                    
            elif self.app_state == "result":
                # Game result events
                action = self.game_result_view.handle_event(event)
                if action == "next_level":
                    self.start_next_level()
                elif action == "play_again":
                    self.result_shown = False  # Reset flag
                    self.start_game(self.current_level)
                elif action == "main_menu":
                    self.return_to_menu()
                    
            elif self.app_state == "game":
                # Game events
                if event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(event)
    
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
                    self.view.show_pause_menu()
            elif self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                if self.view:
                    self.view.hide_pause_menu()
            return
            
        # R to restart when game over
        if event.key == pygame.K_r and self.controller.game_state == GameState.GAME_OVER:
            self.controller.restart_game()
        
        # Handle level complete inputs
        elif self.controller.game_state == GameState.LEVEL_COMPLETE:
            self.controller.handle_level_complete_input(event.key)
        
        # SPACE for alternative pause/unpause
        elif event.key == pygame.K_SPACE:
            if self.controller.game_state == GameState.PLAYING:
                self.controller.pause_game()
                if self.view:
                    self.view.show_pause_menu()
            elif self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                if self.view:
                    self.view.hide_pause_menu()
        
        # Q to quit to menu (new shortcut)
        elif event.key == pygame.K_q:
            self.return_to_menu()
            return
        
        # Debug controls - only work if game is playing
        elif event.key == pygame.K_F1 and self.controller.game_state == GameState.PLAYING:
            self.debug_mode = not self.debug_mode
            print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
        
        elif event.key == pygame.K_F2 and self.controller.game_state == GameState.PLAYING:
            if self.view:
                self.view.toggle_grid()
                print("Grid toggled")
        
        elif event.key == pygame.K_F3:
            # Screenshot - works anytime
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            if self.view:
                self.view.capture_screenshot(filename)
            print(f"Screenshot saved: {filename}")
        
        # AI difficulty controls - only work if game is playing
        elif event.key == pygame.K_1 and self.controller.game_state == GameState.PLAYING:
            if self.controller:
                self.controller.set_ai_difficulty('easy')
                print("AI Difficulty: Easy")
        
        elif event.key == pygame.K_2 and self.controller.game_state == GameState.PLAYING:
            if self.controller:
                self.controller.set_ai_difficulty('medium')
                print("AI Difficulty: Medium")
        
        elif event.key == pygame.K_3 and self.controller.game_state == GameState.PLAYING:
            if self.controller:
                self.controller.set_ai_difficulty('hard')
                print("AI Difficulty: Hard")
        
        elif event.key == pygame.K_3:
            if self.controller:
                self.controller.set_ai_difficulty('hard')
                print("AI Difficulty: Hard")
    
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
                
                # Debug overlay
                if self.debug_mode:
                    self._render_debug_info()
                    
        elif self.app_state == "result":
            # Render game result
            if self.view:
                # Draw game background
                self.view.draw(dt)
            
            # Draw result overlay
            if self.winner == OwnerType.PLAYER:
                all_complete = self.current_level >= 3 and not self.has_next_level
                self.game_result_view.draw_win_screen(
                    self.screen, self.current_level, self.has_next_level, all_complete
                )
            else:
                self.game_result_view.draw_lose_screen(self.screen, self.current_level)
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self):
        """Render debug information overlay"""
        if not self.controller:
            return
            
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
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def _cleanup(self):
        """Clean up resources"""
        print("Cleaning up game resources...")
        pygame.quit()
        sys.exit()

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
