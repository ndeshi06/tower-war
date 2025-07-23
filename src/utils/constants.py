"""
Constants module chứa tất cả các hằng số được sử dụng trong game
"""
import pygame

# Kích thước màn hình
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Màu sắc
class Colors:
    """Class chứa các màu sắc sử dụng trong game"""
    BLUE = (0, 100, 255)      # Màu player
    RED = (255, 50, 50)       # Màu enemy
    GRAY = (128, 128, 128)    # Màu neutral
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 200, 0)       # Màu xanh lá đậm
    LIGHT_GREEN = (144, 238, 144)  # Màu xanh lá nhạt
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (0, 0, 139)
    LIGHT_GRAY = (192, 192, 192)   # Màu xám nhạt

# Cài đặt game
class GameSettings:
    """Class chứa các cài đặt game"""
    FPS = 60
    TOWER_RADIUS = 30
    TOWER_MAX_TROOPS = 50 
    TOWER_GROWTH_RATE = 1
    TROOP_SPEED = 100
    TROOP_RADIUS = 5
    AI_ACTION_INTERVAL = 3000  # milliseconds
    
    # Font sizes
    FONT_LARGE = 36
    FONT_MEDIUM = 24
    FONT_SMALL = 16
    
# Enums cho các trạng thái
class OwnerType:
    """Enum cho các loại chủ sở hữu tower"""
    PLAYER = 'player'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'

class GameState:
    """Enum cho các trạng thái game"""
    PLAYING = 'playing'
    GAME_OVER = 'game_over'
    PAUSED = 'paused'
