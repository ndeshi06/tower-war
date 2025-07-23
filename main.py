"""
Main game application - entry point
Thể hiện MVC Pattern và các OOP principles
"""
import pygame
import sys
from src.controllers.game_controller import GameController
from src.controllers.menu_manager import MenuManager
from src.views.game_view import GameView
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GameSettings, GameState

class TowerWarGame:
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
        
        # Menu manager
        self.menu_manager = MenuManager()
        
        # Game components (MVC Pattern) - lazy initialization
        self.controller = None
        self.view = None
        
        # Game state
        self.in_menu = True
        
        # Game loop components
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = False
        
        # Input handling
        self.keys_pressed = set()
    
    def start_game(self):
        """Khởi tạo game components"""
        if not self.controller:
            # Tạo game components khi cần (Lazy initialization)
            self.controller = GameController()  
            self.view = GameView(self.screen)   
            
            # Setup Observer relationships
            self.controller.attach(self.view)
            
            # Apply settings from menu
            settings = self.menu_manager.get_settings()
            if hasattr(self.controller, 'ai_controller'):
                self.controller.ai_controller.set_difficulty(settings.ai_difficulty)
        
        # Reset game state
        if self.controller:
            self.controller.restart_game()
        
        self.in_menu = False
        print(f"Game started with AI difficulty: {self.menu_manager.get_settings().ai_difficulty}")
        print("Controls: ESC/SPACE=Pause, Q=Quit to menu, R=Restart when game over")
        print("          F1=Debug, F2=Grid, F3=Screenshot, 1/2/3=AI difficulty")
    
    def return_to_menu(self):
        """Quay về menu"""
        self.in_menu = True
        self.menu_manager.reset_to_main()
        print("Returned to main menu")
    
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
        Handle all pygame events
        Strategy Pattern có thể được apply ở đây cho different input handlers
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.in_menu:
                # Menu events
                action = self.menu_manager.handle_event(event)
                if action == "start_game":
                    self.start_game()
                elif action == "quit":
                    self.running = False
            else:
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
        Update game state
        Observer Pattern - controller sẽ notify view về changes
        """
        if not self.in_menu and self.controller:
            self.controller.update(dt)
        
        # Update menu if in menu
        if self.in_menu:
            self.menu_manager.update(dt)
    
    def _render(self, dt):
        """
        Render current frame
        """
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        if self.in_menu:
            # Render menu
            self.menu_manager.render(self.screen)
        else:
            # Render game
            if self.view:
                self.view.draw(dt)
                
                # Debug overlay
                if self.debug_mode:
                    self._render_debug_info()
        
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
            f"Game State: {self.controller.game_state.name}",
            f"Player Towers: {len([t for t in self.controller.towers if t.owner == 'player'])}",
            f"Enemy Towers: {len([t for t in self.controller.towers if t.owner == 'enemy'])}",
            f"Neutral Towers: {len([t for t in self.controller.towers if t.owner == 'neutral'])}",
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
