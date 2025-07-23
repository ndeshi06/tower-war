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
        pygame.display.set_caption("Tower War - OOP Edition")
        
        # Menu manager
        self.menu_manager = MenuManager()
        
        # Game components (MVC Pattern) - tạo khi cần
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
            
            elif event.type == pygame.KEYDOWN:
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
        
        # Game controls
        if event.key == pygame.K_r and self.controller.game_state == GameState.GAME_OVER:
            self.controller.restart_game()
        
        elif event.key == pygame.K_ESCAPE:
            if self.controller.game_state == GameState.PLAYING:
                self.controller.pause_game()
                self.view.show_pause_menu()
            elif self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                self.view.hide_pause_menu()
        
        elif event.key == pygame.K_SPACE:
            if self.controller.game_state == GameState.PAUSED:
                self.controller.pause_game()
                self.view.hide_pause_menu()
        
        # Debug controls
        elif event.key == pygame.K_F1:
            self.debug_mode = not self.debug_mode
        
        elif event.key == pygame.K_F2:
            self.view.toggle_grid()
        
        elif event.key == pygame.K_F3:
            # Screenshot
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            self.view.capture_screenshot(filename)
            print(f"Screenshot saved: {filename}")
        
        # AI difficulty controls
        elif event.key == pygame.K_1:
            self.controller.set_ai_difficulty('easy')
            print("AI Difficulty: Easy")
        
        elif event.key == pygame.K_2:
            self.controller.set_ai_difficulty('medium')
            print("AI Difficulty: Medium")
        
        elif event.key == pygame.K_3:
            self.controller.set_ai_difficulty('hard')
            print("AI Difficulty: Hard")
    
    def _handle_keyup(self, event):
        """Handle key release events"""
        if event.key in self.keys_pressed:
            self.keys_pressed.remove(event.key)
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events"""
        if event.button == 1:  # Left click
            # Check UI clicks first
            ui_action = self.view.handle_ui_click(event.pos)
            
            if ui_action == "restart":
                self.controller.restart_game()
            elif ui_action == "resume":
                self.controller.pause_game()
                self.view.hide_pause_menu()
            elif ui_action == "menu":
                # Could implement main menu here
                print("Menu not implemented yet")
            
            # If no UI action, handle game clicks
            elif ui_action is None and self.controller.game_state == GameState.PLAYING:
                self.controller.handle_click(event.pos)
    
    def _handle_mouse_motion(self, event):
        """Handle mouse motion for hover effects"""
        self.view.update_mouse_position(event.pos)
    
    def _update(self, dt: float):
        """
        Update game logic
        """
        if self.controller.game_state == GameState.PLAYING:
            # Update game controller
            self.controller.update(dt)
            
            # Update view with current game state
            self.view.set_towers(self.controller.towers)
            self.view.set_troops(self.controller.troops)
            
            # Update HUD with game stats
            game_stats = self.controller.get_game_stats()
            self.view.update_hud_stats(game_stats)
    
    def _render(self, dt: float):
        """
        Render everything to screen
        """
        # Main rendering
        self.view.draw(dt)
        
        # Debug information
        if self.debug_mode:
            debug_info = self._get_debug_info()
            self.view.draw_debug_info(debug_info)
    
    def _get_debug_info(self) -> dict:
        """Get debug information"""
        game_stats = self.controller.get_game_stats()
        
        return {
            "FPS": int(self.clock.get_fps()),
            "Game State": self.controller.game_state,
            "Towers": len(self.controller.towers),
            "Troops": len(self.controller.troops),
            "Player Actions": game_stats.get('player_actions', 0),
            "AI Difficulty": game_stats.get('ai_stats', {}).get('difficulty', 'unknown'),
            "Selected Tower": self.controller.selected_tower is not None
        }
    
    def _cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")
        pygame.quit()
        sys.exit()

def main():
    """
    Entry point of the application
    """
    try:
        game = TowerWarGame()
        game.run()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
