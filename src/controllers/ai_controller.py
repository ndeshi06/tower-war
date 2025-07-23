"""
AI Controller - thể hiện Strategy Pattern và Observer Pattern
"""
import pygame
import random
import math
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.base import Observer, Subject
from ..models.tower import Tower, EnemyTower
from ..models.troop import EnemyTroop
from ..utils.constants import OwnerType, GameSettings

class AIStrategy(ABC):
    """
    Abstract strategy class cho AI behavior
    Thể hiện Strategy Pattern
    """
    
    @abstractmethod
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """
        Quyết định hành động của AI
        Returns: dict với 'source', 'target' towers nếu có action
        """
        pass

class AggressiveStrategy(AIStrategy):
    """
    Aggressive AI strategy - tấn công liên tục
    """
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Aggressive strategy - tấn công tower gần nhất của player"""
        if not enemy_towers:
            return None
        
        # Tìm towers có thể tấn công (có quân > 1)
        available_towers = [t for t in enemy_towers if t.troops > 1]
        if not available_towers:
            return None
        
        # Chọn tower có nhiều quân nhất
        source_tower = max(available_towers, key=lambda t: t.troops)
        
        # Tìm player towers để tấn công
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        
        targets = player_towers + neutral_towers
        if not targets:
            return None
        
        # Chọn target gần nhất
        target = min(targets, key=lambda t: source_tower.distance_to(t))
        
        return {'source': source_tower, 'target': target}

class DefensiveStrategy(AIStrategy):
    """
    Defensive AI strategy - tập trung bảo vệ và mở rộng từ từ
    """
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Defensive strategy - ưu tiên chiếm neutral towers gần"""
        if not enemy_towers:
            return None
        
        available_towers = [t for t in enemy_towers if t.troops > 5]  # Cần nhiều quân hơn
        if not available_towers:
            return None
        
        # Ưu tiên neutral towers trước
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        
        if neutral_towers:
            # Chọn source tower gần neutral tower nhất
            best_pair = None
            min_distance = float('inf')
            
            for source in available_towers:
                for target in neutral_towers:
                    distance = source.distance_to(target)
                    if distance < min_distance:
                        min_distance = distance
                        best_pair = {'source': source, 'target': target}
            
            return best_pair
        
        # Nếu không có neutral towers, tấn công player towers yếu
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        if player_towers:
            # Chọn player tower có ít quân nhất
            weak_target = min(player_towers, key=lambda t: t.troops)
            # Chọn source tower gần nhất
            source = min(available_towers, key=lambda t: t.distance_to(weak_target))
            return {'source': source, 'target': weak_target}
        
        return None

class SmartStrategy(AIStrategy):
    """
    Smart AI strategy - kết hợp aggressive và defensive
    """
    
    def __init__(self):
        self.consecutive_failures = 0
        self.last_success_time = pygame.time.get_ticks()
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Smart strategy - thay đổi chiến thuật dựa trên tình hình"""
        if not enemy_towers:
            return None
        
        available_towers = [t for t in enemy_towers if t.troops > 1]
        if not available_towers:
            return None
        
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        
        # Đánh giá tình hình
        enemy_strength = sum(t.troops for t in enemy_towers)
        player_strength = sum(t.troops for t in player_towers)
        
        # Nếu AI mạnh hơn, aggressive
        if enemy_strength > player_strength * 1.2:
            return self._aggressive_action(available_towers, player_towers + neutral_towers)
        # Nếu AI yếu hơn, defensive
        elif enemy_strength < player_strength * 0.8:
            return self._defensive_action(available_towers, neutral_towers, player_towers)
        # Nếu cân bằng, mixed strategy
        else:
            return self._mixed_action(available_towers, player_towers, neutral_towers)
    
    def _aggressive_action(self, sources: List[Tower], targets: List[Tower]) -> Optional[dict]:
        """Aggressive action"""
        if not sources or not targets:
            return None
        
        # Chọn source tower mạnh nhất
        source = max(sources, key=lambda t: t.troops)
        # Chọn target yếu nhất
        target = min(targets, key=lambda t: t.troops)
        
        return {'source': source, 'target': target}
    
    def _defensive_action(self, sources: List[Tower], neutral_targets: List[Tower], 
                         player_targets: List[Tower]) -> Optional[dict]:
        """Defensive action"""
        if not sources:
            return None
        
        # Ưu tiên neutral towers
        if neutral_targets:
            source = max(sources, key=lambda t: t.troops)
            target = min(neutral_targets, key=lambda t: 
                        source.distance_to(t) + t.troops * 0.1)  # Ưu tiên gần và ít quân
            return {'source': source, 'target': target}
        
        # Nếu không có neutral, tấn công player tower yếu nhất
        if player_targets:
            weak_target = min(player_targets, key=lambda t: t.troops)
            source = min(sources, key=lambda t: t.distance_to(weak_target))
            return {'source': source, 'target': weak_target}
        
        return None
    
    def _mixed_action(self, sources: List[Tower], player_targets: List[Tower], 
                     neutral_targets: List[Tower]) -> Optional[dict]:
        """Mixed strategy action"""
        all_targets = player_targets + neutral_targets
        if not sources or not all_targets:
            return None
        
        # Random choice giữa aggressive và defensive
        if random.choice([True, False]):
            return self._aggressive_action(sources, all_targets)
        else:
            return self._defensive_action(sources, neutral_targets, player_targets)

class AIController(Observer, Subject):
    """
    AI Controller class - thể hiện Observer Pattern và Strategy Pattern
    """
    
    def __init__(self, difficulty: str = 'medium'):
        Observer.__init__(self)
        Subject.__init__(self)
        self.last_action_time = pygame.time.get_ticks()
        self.action_interval = GameSettings.AI_ACTION_INTERVAL
        self.difficulty = difficulty
        
        # Strategy Pattern - chọn strategy dựa trên difficulty
        self.strategy = self._create_strategy(difficulty)
        
        # Statistics tracking
        self.actions_taken = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
    
    def _create_strategy(self, difficulty: str) -> AIStrategy:
        """Factory method để tạo AI strategy - Factory Pattern"""
        strategies = {
            'easy': DefensiveStrategy(),
            'medium': SmartStrategy(),
            'hard': AggressiveStrategy()
        }
        return strategies.get(difficulty, SmartStrategy())
    
    def set_difficulty(self, difficulty: str):
        """Thay đổi độ khó AI"""
        self.difficulty = difficulty
        self.strategy = self._create_strategy(difficulty)
        
        # Adjust action interval based on difficulty
        intervals = {
            'easy': 4000,    # 4 seconds
            'medium': 3000,  # 3 seconds  
            'hard': 2000     # 2 seconds
        }
        self.action_interval = intervals.get(difficulty, 3000)
    
    def update_observer(self, event_type: str, data: dict):
        """
        Implementation của Observer interface
        Respond to game events
        """
        if event_type == "tower_captured":
            if data.get("new_owner") == OwnerType.ENEMY:
                self.successful_attacks += 1
            elif data.get("old_owner") == OwnerType.ENEMY:
                self.failed_attacks += 1
        
        elif event_type == "game_started":
            self.reset_stats()
    
    def should_take_action(self) -> bool:
        """Kiểm tra xem AI có nên hành động không"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_action_time >= self.action_interval
    
    def execute_action(self, towers: List[Tower]) -> Optional['EnemyTroop']:
        """
        Thực hiện hành động AI
        Returns: EnemyTroop nếu có action được thực hiện
        """
        if not self.should_take_action():
            return None
        
        enemy_towers = [t for t in towers if t.owner == OwnerType.ENEMY]
        if not enemy_towers:
            return None
        
        # Sử dụng strategy để quyết định action
        action = self.strategy.decide_action(enemy_towers, towers)
        
        if action:
            source_tower = action['source']
            target_tower = action['target']
            
            # Thực hiện gửi quân
            troops_count = source_tower.send_troops(target_tower)
            
            if troops_count > 0:
                # Tạo enemy troop
                troop = EnemyTroop(
                    source_tower.x, source_tower.y,
                    target_tower.x, target_tower.y,
                    troops_count
                )
                
                self.actions_taken += 1
                self.last_action_time = pygame.time.get_ticks()
                
                # Notify observers về AI action
                self.notify("ai_action_taken", {
                    "source": source_tower,
                    "target": target_tower,
                    "troops_count": troops_count,
                    "strategy": self.strategy.__class__.__name__
                })
                
                return troop
        
        self.last_action_time = pygame.time.get_ticks()
        return None
    
    def reset_stats(self):
        """Reset AI statistics"""
        self.actions_taken = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        self.last_action_time = pygame.time.get_ticks()
    
    def get_performance_stats(self) -> dict:
        """Lấy thống kê hiệu suất AI"""
        total_attacks = self.successful_attacks + self.failed_attacks
        success_rate = (self.successful_attacks / total_attacks * 100) if total_attacks > 0 else 0
        
        return {
            'actions_taken': self.actions_taken,
            'successful_attacks': self.successful_attacks,
            'failed_attacks': self.failed_attacks,
            'success_rate': success_rate,
            'difficulty': self.difficulty
        }
    
    def __str__(self) -> str:
        """String representation of AI controller"""
        stats = self.get_performance_stats()
        return (f"AIController(difficulty={self.difficulty}, "
                f"actions={stats['actions_taken']}, "
                f"success_rate={stats['success_rate']:.1f}%)")
