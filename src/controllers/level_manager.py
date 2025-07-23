"""
Level Manager - quản lý progression của game levels
"""
from typing import Dict, Any
from ..utils.constants import LevelConfig

class LevelManager:
    """
    Quản lý các level trong game
    Thể hiện State Pattern cho level progression
    """
    
    def __init__(self):
        self.current_level = 1
        self.max_level = 3
        self.levels_completed = set()
        
        # Level configurations
        self.level_configs = {
            1: LevelConfig.LEVEL_1,
            2: LevelConfig.LEVEL_2, 
            3: LevelConfig.LEVEL_3
        }
    
    def get_current_level_config(self) -> Dict[str, Any]:
        """Lấy cấu hình của level hiện tại"""
        return self.level_configs.get(self.current_level, LevelConfig.LEVEL_1)
    
    def set_level(self, level: int):
        """Set level hiện tại"""
        if level in self.level_configs:
            self.current_level = level
            print(f"Level set to {level}: {self.get_current_level_config()['name']}")
        else:
            print(f"Invalid level {level}, staying at {self.current_level}")
    
    def complete_current_level(self) -> bool:
        """
        Hoàn thành level hiện tại
        Returns: True nếu có level tiếp theo, False nếu đã hoàn thành hết
        """
        completed_level = self.current_level
        self.levels_completed.add(completed_level)
        
        if completed_level < self.max_level:
            print(f"Level {completed_level} completed! Next level available: {completed_level + 1}")
            return True
        else:
            print("Congratulations! You completed all levels!")
            return False
    
    def advance_to_next_level(self):
        """Chuyển sang level tiếp theo"""
        if self.current_level < self.max_level:
            self.current_level += 1
            print(f"Advanced to {self.get_current_level_config()['name']}")
            return True
        return False
    
    def reset_to_level_1(self):
        """Reset về level 1 khi thua"""
        self.current_level = 1
        self.levels_completed.clear()
        print("Game Over! Returning to Level 1")
    
    def get_level_info(self) -> str:
        """Lấy thông tin level hiện tại"""
        config = self.get_current_level_config()
        return f"{config['name']} - AI: {config['ai_difficulty'].upper()}"
    
    def is_final_level(self) -> bool:
        """Kiểm tra có phải level cuối không"""
        return self.current_level >= self.max_level
    
    def get_progress(self) -> str:
        """Lấy tiến độ hoàn thành"""
        return f"Level {self.current_level}/{self.max_level}"
