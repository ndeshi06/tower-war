"""
Image Manager - quản lý tất cả images trong game
Thể hiện Singleton Pattern để cache images
"""
import pygame
import os
from typing import Dict, Optional
from ..utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class ImageManager:
    """
    Singleton Image Manager
    Cache và quản lý tất cả images trong game
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.images: Dict[str, pygame.Surface] = {}
        self.image_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'images')
        self._initialized = True
    
    def load_image(self, filename: str, size: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """
        Load image từ file
        Args:
            filename: tên file trong images folder
            size: (width, height) để resize, None để giữ nguyên
        """
        if filename in self.images:
            return self.images[filename]
        
        filepath = os.path.join(self.image_folder, filename)
        
        try:
            # Load image
            image = pygame.image.load(filepath).convert_alpha()
            
            # Resize nếu cần
            if size:
                image = pygame.transform.scale(image, size)
            
            # Cache image
            self.images[filename] = image
            print(f"Loaded image: {filename}")
            return image
            
        except pygame.error as e:
            print(f"Could not load image {filename}: {e}")
            return None
    
    def get_background(self) -> Optional[pygame.Surface]:
        """Get background image"""
        return self.load_image('background.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def get_tower_image(self, tower_type: str) -> Optional[pygame.Surface]:
        """
        Get tower image based on type
        Args:
            tower_type: 'player', 'enemy', 'neutral'
        """
        filename_map = {
            'player': 'tower_player.png',
            'enemy': 'tower_enemy.png', 
            'neutral': 'tower_neutral.png'
        }
        
        filename = filename_map.get(tower_type)
        if filename:
            return self.load_image(filename, (60, 60))  # Tower size 60x60
        return None
    
    def create_placeholder_image(self, size: tuple, color: tuple) -> pygame.Surface:
        """
        Tạo placeholder image khi không có file
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface
    
    def get_image(self, image_name: str, size: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """
        Generic method để get image theo tên
        Tự động map tên đến filename tương ứng
        """
        # Map image names to filenames
        name_to_file = {
            'background_menu': 'background_menu.png',
            'background_game': 'background_game.png',
            'tower_player': 'tower_player.png',
            'tower_enemy': 'tower_enemy.png', 
            'tower_neutral': 'tower_neutral.png'
        }
        
        filename = name_to_file.get(image_name)
        if filename:
            # Determine size based on image type
            if not size:
                if 'background' in image_name:
                    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
                elif 'tower' in image_name:
                    size = (60, 60)
            
            return self.load_image(filename, size)
        
        # If no mapping found, try loading directly
        return self.load_image(f"{image_name}.png", size)

    def get_tower_placeholder(self, tower_type: str) -> pygame.Surface:
        """Get placeholder tower image khi không có file"""
        from ..utils.constants import Colors
        
        color_map = {
            'player': Colors.BLUE,
            'enemy': Colors.RED,
            'neutral': Colors.GRAY
        }
        
        color = color_map.get(tower_type, Colors.GRAY)
        return self.create_placeholder_image((60, 60), color)
    
    def clear_cache(self):
        """Clear image cache"""
        self.images.clear()
        print("Image cache cleared")
