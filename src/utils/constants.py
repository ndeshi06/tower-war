"""
Constants module chứa tất cả các hằng số được sử dụng trong game
"""
import pygame

# Kích thước màn hình
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576

# Kích thước vật thể
TOWER_SIZE = (64, 64)

# Màu sắc
class Colors:
    """Class chứa các màu sắc sử dụng trong game"""
    BLUE = (0, 100, 255)      # Màu player
    RED = (255, 50, 50)       # Màu enemy
    GRAY = (128, 128, 128)    # Màu neutral
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 200, 0)       # Màu xanh lá đậm
    ORANGE = (255, 165, 0)    # Màu cam cho nút CONTINUE
    LIGHT_GREEN = (144, 238, 144)  # Màu xanh lá nhạt
    LIGHT_RED = (255, 182, 193)    # Màu đỏ nhạt
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
    TROOP_RADIUS = 12
    AI_ACTION_INTERVAL = 2500  # milliseconds - tăng tốc độ phản hồi của AI
    
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
    LEVEL_COMPLETE = 'level_complete'

class LevelConfig:
    """Level configuration"""
    LEVEL_1 = {
        'name': 'Level 1 - Easy',
        'ai_difficulty': 'easy',
        'player_towers': 3,
        'enemy_towers': 2,
        'neutral_towers': 2,
        'initial_troops': 20,
        'enemy_initial_troops': 10 
    }
    
    LEVEL_2 = {
        'name': 'Level 2 - Medium', 
        'ai_difficulty': 'medium',
        'player_towers': 2,
        'enemy_towers': 3,
        'neutral_towers': 3,
        'initial_troops': 25,
        'enemy_initial_troops': 12 
    }
    
    LEVEL_3 = {
        'name': 'Level 3 - Hard',
        'ai_difficulty': 'hard',
        'player_towers': 2,
        'enemy_towers': 4,
        'neutral_towers': 2,
        'initial_troops': 30,
        'enemy_initial_troops': 20 
    }
