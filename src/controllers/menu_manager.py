"""
Menu Manager - quản lý navigation giữa các menu
Thể hiện State Pattern và Facade Pattern
"""
import pygame
from enum import Enum
from typing import Optional
from ..views.main_menu import MainMenu
from ..views.settings_menu import SettingsMenu
from ..views.help_menu import HelpMenu
from ..utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class MenuState(Enum):
    """Enum cho các trạng thái menu"""
    MAIN = "main"
    SETTINGS = "settings"
    HELP = "help"
    GAME = "game"

class MenuManager:
    """
    Menu Manager class
    Thể hiện State Pattern cho menu navigation
    """
    
    def __init__(self):
        # Current state
        self.current_state = MenuState.MAIN
        
        # Menu instances
        self.main_menu = MainMenu()
        self.settings_menu = SettingsMenu()
        self.help_menu = HelpMenu()
        
        # Initially only main menu is visible
        self._update_visibility()
    
    def _update_visibility(self):
        """Update visibility của các menu dựa trên current state"""
        self.main_menu.visible = (self.current_state == MenuState.MAIN)
        self.settings_menu.visible = (self.current_state == MenuState.SETTINGS)
        self.help_menu.visible = (self.current_state == MenuState.HELP)
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """
        Handle click events và state transitions
        Returns: action string hoặc None
        """
        if self.current_state == MenuState.MAIN:
            action = self.main_menu.handle_click(pos)
            
            if action == "start_game":
                self.current_state = MenuState.GAME
                return "start_game"
            elif action == "settings":
                self.current_state = MenuState.SETTINGS
                self._update_visibility()
            elif action == "help":
                self.current_state = MenuState.HELP
                self._update_visibility()
            elif action == "quit":
                return "quit"
        
        elif self.current_state == MenuState.SETTINGS:
            action = self.settings_menu.handle_click(pos)
            
            if action == "back":
                self.current_state = MenuState.MAIN
                self._update_visibility()
            elif action in ["ai_easy", "ai_medium", "ai_hard"]:
                return action  # Pass to game controller
            elif action in ["toggle_sound", "toggle_music"]:
                return action  # Pass to audio manager (if implemented)
        
        elif self.current_state == MenuState.HELP:
            action = self.help_menu.handle_click(pos)
            
            if action == "back":
                self.current_state = MenuState.MAIN
                self._update_visibility()
        
        return None
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.update_mouse_pos(event.pos)
        elif event.type == pygame.KEYDOWN:
            return self.handle_key(event.key)
        
        return None
    
    def handle_key(self, key: int) -> Optional[str]:
        """Handle keyboard input trong menu"""
        if key == pygame.K_ESCAPE:
            if self.current_state != MenuState.MAIN:
                self.current_state = MenuState.MAIN
                self._update_visibility()
        
        return None
    
    def update_mouse_pos(self, pos: tuple):
        """Update mouse position cho tất cả menus"""
        self.main_menu.update_mouse_pos(pos)
        self.settings_menu.update_mouse_pos(pos)
        self.help_menu.update_mouse_pos(pos)
    
    def draw(self, screen: pygame.Surface):
        """Vẽ current menu"""
        if self.current_state == MenuState.MAIN:
            self.main_menu.draw(screen)
        elif self.current_state == MenuState.SETTINGS:
            # Draw main menu as background
            self.main_menu.draw(screen)
            self.settings_menu.draw(screen)
        elif self.current_state == MenuState.HELP:
            # Draw main menu as background
            self.main_menu.draw(screen)
            self.help_menu.draw(screen)
    
    def is_in_game(self) -> bool:
        """Check xem có đang trong game không"""
        return self.current_state == MenuState.GAME
    
    def show_main_menu(self):
        """Hiện main menu (từ game)"""
        self.current_state = MenuState.MAIN
        self._update_visibility()
    
    def get_ai_difficulty(self) -> str:
        """Get current AI difficulty setting"""
        return self.settings_menu.ai_difficulty
    
    def is_sound_enabled(self) -> bool:
        """Get sound setting"""
        return self.settings_menu.sound_enabled
    
    def is_music_enabled(self) -> bool:
        """Get music setting"""
        return self.settings_menu.music_enabled
    
    def get_settings(self):
        """Get current settings as object"""
        class Settings:
            def __init__(self, ai_difficulty, sound_enabled, music_enabled):
                self.ai_difficulty = ai_difficulty
                self.sound_enabled = sound_enabled
                self.music_enabled = music_enabled
        
        return Settings(
            ai_difficulty=self.get_ai_difficulty(),
            sound_enabled=self.is_sound_enabled(),
            music_enabled=self.is_music_enabled()
        )
    
    def reset_to_main(self):
        """Reset về main menu"""
        self.current_state = MenuState.MAIN
        self._update_visibility()
    
    def update(self, dt: float):
        """Update menu animations (if any)"""
        # Could be used for menu animations in the future
        pass
    
    def render(self, screen: pygame.Surface):
        """Render current menu (alias for draw)"""
        self.draw(screen)
