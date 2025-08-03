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
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Fast aggressive strategy - optimized for level 2 & 3"""
        if not enemy_towers:
            print("AggressiveStrategy: No enemy towers")
            return None
        
        # Lower requirements for faster actions
        available_towers = [t for t in enemy_towers if t.troops > 0]
        if not available_towers:
            print(f"AggressiveStrategy: No available towers. Enemy towers: {[(t.x, t.y, t.troops) for t in enemy_towers]}")
            return None
        
        # Find targets (prefer player towers)
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        all_targets = player_towers + neutral_towers
        
        if not all_targets:
            print("AggressiveStrategy: No targets")
            return None
        
        # Fast target selection: strongest tower attacks best target
        best_action = self._find_best_attack(available_towers, all_targets)
        
        if best_action:
            print(f"AggressiveStrategy: Tower at ({best_action['source'].x}, {best_action['source'].y}) with {best_action['source'].troops} troops attacking ({best_action['target'].x}, {best_action['target'].y})")
            return best_action
        
        # Fallback: any tower attacks closest target
        strongest_tower = max(available_towers, key=lambda t: t.troops)
        closest_target = min(all_targets, key=lambda t: strongest_tower.distance_to(t))
        
        print(f"AggressiveStrategy: Fallback - Tower at ({strongest_tower.x}, {strongest_tower.y}) attacking ({closest_target.x}, {closest_target.y})")
        
        return {
            'source': strongest_tower,
            'target': closest_target,
            'type': 'single_attack'
        }
    
    def _find_best_attack(self, available_towers: List[Tower], targets: List[Tower]) -> Optional[dict]:
        """Find the best single attack opportunity - optimized for speed"""
        best_score = 0
        best_attack = None
        
        for source in available_towers:
            if source.troops <= 0:
                continue
                
            for target in targets:
                # Quick scoring system
                distance = source.distance_to(target)
                if distance > 400:  # Skip very far targets
                    continue
                
                # Priority: player towers > neutral towers
                target_priority = 2.0 if target.owner == OwnerType.PLAYER else 1.0
                
                # Prefer weaker targets
                troops_advantage = max(0, source.troops - target.troops)
                
                # Distance factor (closer is better)
                distance_factor = 1.0 / max(distance, 1) * 100
                
                # Combined score
                score = target_priority * 10 + troops_advantage + distance_factor
                
                if score > best_score:
                    best_score = score
                    best_attack = {
                        'source': source,
                        'target': target,
                        'type': 'single_attack'
                    }
        
        return best_attack
    
    def _select_strategic_target(self, targets: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn target có giá trị chiến lược cao nhất"""
        def target_priority(target):
            # Ưu tiên tower có ít quân (dễ chiếm)
            troops_factor = 1.0 / max(target.troops, 1)
            
            # Ưu tiên tower gần nhiều enemy towers (có thể hỗ trợ)
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 200)
            support_factor = nearby_support * 0.3
            
            # Ưu tiên player towers hơn neutral
            owner_factor = 2.0 if target.owner == OwnerType.PLAYER else 1.0
            
            return troops_factor + support_factor + owner_factor
        
        return max(targets, key=target_priority)
    
    def _find_coordinated_attackers(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tìm towers có thể phối hợp tấn công"""
        # Sắp xếp towers theo khoảng cách đến target
        towers_by_distance = sorted(available_towers, 
                                  key=lambda t: t.distance_to(target))
        
        coordinated = []
        max_attackers = min(3, len(towers_by_distance))  # Tối đa 3 towers cùng lúc
        
        for tower in towers_by_distance[:max_attackers]:
            if tower.distance_to(target) < 300:  # Trong phạm vi hỗ trợ
                coordinated.append(tower)
        
        return coordinated if coordinated else [towers_by_distance[0]]

class DefensiveStrategy(AIStrategy):
    """
    Defensive AI strategy - tập trung bảo vệ và mở rộng với multi-tower coordination
    """
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Defensive strategy - simplified"""
        if not enemy_towers:
            return None
        
        # Simple requirement
        available_towers = [t for t in enemy_towers if t.troops > 1]
        if not available_towers:
            return None
        
        # Find targets (prefer neutral)
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        targets = neutral_towers if neutral_towers else player_towers
        
        if not targets:
            return None
        
        # Simple action
        source = max(available_towers, key=lambda t: t.troops)
        target = min(targets, key=lambda t: source.distance_to(t))
        
        return {
            'source': source,
            'target': target,
            'type': 'single_attack'
        }
    
    def _select_expansion_target(self, neutral_towers: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn neutral tower tốt nhất để mở rộng"""
        def expansion_value(target):
            # Ưu tiên tower có ít quân
            troops_factor = 1.0 / max(target.troops, 1)
            
            # Ưu tiên tower gần nhiều enemy towers (dễ hỗ trợ)
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 250)
            support_factor = nearby_support * 0.4
            
            # Ưu tiên tower ở vị trí trung tâm
            center_distance = math.sqrt((target.x - 400)**2 + (target.y - 300)**2)
            center_factor = 1.0 / max(center_distance, 1) * 100
            
            return troops_factor + support_factor + center_factor
        
        return max(neutral_towers, key=expansion_value)
    
    def _select_defensive_target(self, player_towers: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn player tower để defensive attack"""
        def defensive_priority(target):
            # Ưu tiên tower yếu
            troops_factor = 1.0 / max(target.troops, 1)
            
            # Ưu tiên tower có nhiều enemy towers gần (có thể hỗ trợ)
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 200)
            support_factor = nearby_support * 0.5
            
            return troops_factor + support_factor
        
        return max(player_towers, key=defensive_priority)
    
    def _find_coordinated_expanders(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tìm towers để coordinated expansion"""
        towers_by_value = []
        
        for tower in available_towers:
            distance = tower.distance_to(target)
            if distance < 280:  # Trong phạm vi expansion
                # Tính giá trị của tower này cho expansion
                value = tower.troops * 0.3 + (1.0 / max(distance, 1)) * 100
                towers_by_value.append((tower, value))
        
        # Sắp xếp theo giá trị và chọn tối đa 2 towers
        towers_by_value.sort(key=lambda x: x[1], reverse=True)
        max_expanders = min(2, len(towers_by_value))
        
        return [tower for tower, _ in towers_by_value[:max_expanders]]
    
    def _find_coordinated_attackers(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tìm towers để coordinated attack (defensive)"""
        towers_by_distance = sorted(available_towers, 
                                  key=lambda t: t.distance_to(target))
        
        coordinated = []
        max_attackers = min(2, len(towers_by_distance))  # Conservative approach
        
        for tower in towers_by_distance[:max_attackers]:
            if tower.distance_to(target) < 250:
                coordinated.append(tower)
        
        return coordinated if coordinated else [towers_by_distance[0]]

class SmartStrategy(AIStrategy):
    """
    Smart AI strategy - advanced multi-tower coordination with adaptive tactics
    """
    
    def __init__(self, difficulty: str = 'medium'):
        self.consecutive_failures = 0
        self.last_success_time = pygame.time.get_ticks()
        self.tactical_mode = "balanced"  # "aggressive", "defensive", "balanced"
        self.mode_change_cooldown = 0
        self.difficulty = difficulty  # Store difficulty level
    
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        """Smart strategy với advanced multi-tower tactics"""
        if not enemy_towers:
            print("SmartStrategy: No enemy towers available")
            return None
        
        available_towers = [t for t in enemy_towers if t.troops > 0]  # Chỉ cần > 0 thay vì > 1
        print(f"SmartStrategy: {len(available_towers)} available towers from {len(enemy_towers)} enemy towers")
        
        if not available_towers:
            print("SmartStrategy: No available towers with enough troops")
            return None
        
        player_towers = [t for t in all_towers if t.owner == OwnerType.PLAYER]
        neutral_towers = [t for t in all_towers if t.owner == OwnerType.NEUTRAL]
        
        print(f"SmartStrategy: Targets - {len(player_towers)} player, {len(neutral_towers)} neutral")
        
        # Adaptive tactical mode switching
        self._update_tactical_mode(enemy_towers, player_towers, neutral_towers)
        
        # Đánh giá tình hình và chọn action type
        action_type = self._analyze_situation(enemy_towers, player_towers, neutral_towers)
        print(f"SmartStrategy: Chosen action type: {action_type}")
        
        if action_type == "coordinated_assault":
            # Coordinated assault can target both player and neutral towers
            all_targets = player_towers + neutral_towers
            result = self._coordinated_assault(available_towers, all_targets)
        elif action_type == "strategic_expansion":
            result = self._strategic_expansion(available_towers, neutral_towers)
        elif action_type == "defensive_consolidation":
            result = self._defensive_consolidation(available_towers, player_towers, neutral_towers)
        else:
            result = self._opportunistic_strike(available_towers, player_towers + neutral_towers)
        
        print(f"SmartStrategy: Action result: {result is not None}")
        return result
    
    def _update_tactical_mode(self, enemy_towers: List[Tower], player_towers: List[Tower], neutral_towers: List[Tower]):
        """Cập nhật chế độ chiến thuật dựa trên tình hình"""
        current_time = pygame.time.get_ticks()
        
        if current_time < self.mode_change_cooldown:
            return
        
        enemy_strength = sum(t.troops for t in enemy_towers)
        player_strength = sum(t.troops for t in player_towers)
        
        # Chế độ aggressive khi AI mạnh hơn nhiều
        if enemy_strength > player_strength * 1.5:
            self.tactical_mode = "aggressive"
        # Chế độ defensive khi AI yếu hơn
        elif enemy_strength < player_strength * 0.7:
            self.tactical_mode = "defensive"
        else:
            self.tactical_mode = "balanced"
        
        # Cooldown để tránh đổi mode quá thường xuyên
        self.mode_change_cooldown = current_time + 5000  # 5 seconds
    
    def _analyze_situation(self, enemy_towers: List[Tower], player_towers: List[Tower], neutral_towers: List[Tower]) -> str:
        """Phân tích tình hình để quyết định action type - Simple logic for all levels"""
        available_towers = [t for t in enemy_towers if t.troops > 1]
        
        # Simple random selection between coordination and single attacks
        if len(available_towers) >= 2 and random.random() > 0.7:  # 30% chance for multi-tower
            return "coordinated_assault"
        elif neutral_towers and random.random() > 0.5:
            return "strategic_expansion"
        else:
            return "opportunistic_strike"
    
    def _coordinated_assault(self, available_towers: List[Tower], targets: List[Tower]) -> Optional[dict]:
        """Tấn công phối hợp với nhiều towers - Enhanced to target any available targets"""
        if not targets:
            print("_coordinated_assault: No targets available")
            return None
        
        print(f"_coordinated_assault: {len(available_towers)} available towers, {len(targets)} targets")
        
        # Chọn target có giá trị cao nhất
        priority_target = self._select_assault_target(targets, available_towers)
        print(f"_coordinated_assault: Selected target at ({priority_target.x}, {priority_target.y}) with {priority_target.troops} troops, owner={priority_target.owner}")
        
        # Tìm towers có thể tham gia assault
        assault_force = self._assemble_assault_force(available_towers, priority_target)
        print(f"_coordinated_assault: Assembled force of {len(assault_force)} towers")
        
        if not assault_force:
            print("_coordinated_assault: No assault force assembled")
            return None
        
        return {
            'sources': assault_force,
            'target': priority_target,
            'type': 'coordinated_assault'
        }
    
    def _strategic_expansion(self, available_towers: List[Tower], neutral_targets: List[Tower]) -> Optional[dict]:
        """Mở rộng chiến lược với coordination - Enhanced to ensure multi-tower"""
        if not neutral_targets:
            print("_strategic_expansion: No neutral targets")
            return None
        
        print(f"_strategic_expansion: {len(available_towers)} available towers, {len(neutral_targets)} neutral targets")
        
        # Chọn neutral tower tốt nhất để expansion
        expansion_target = self._select_expansion_target(neutral_targets, available_towers)
        print(f"_strategic_expansion: Selected target at ({expansion_target.x}, {expansion_target.y}) with {expansion_target.troops} troops")
        
        # Tìm towers để support expansion
        expansion_force = self._assemble_expansion_force(available_towers, expansion_target)
        print(f"_strategic_expansion: Assembled force of {len(expansion_force)} towers")
        
        if not expansion_force:
            print("_strategic_expansion: No expansion force assembled")
            return None
        
        return {
            'sources': expansion_force,
            'target': expansion_target,
            'type': 'strategic_expansion'
        }
    
    def _defensive_consolidation(self, available_towers: List[Tower], player_targets: List[Tower], neutral_targets: List[Tower]) -> Optional[dict]:
        """Consolidation và defensive moves"""
        # Ưu tiên neutral nếu có
        targets = neutral_targets if neutral_targets else player_targets
        if not targets:
            return None
        
        # Chọn target an toàn nhất
        safe_target = self._select_safe_target(targets, available_towers)
        
        # Conservative force selection
        conservative_force = self._assemble_conservative_force(available_towers, safe_target)
        
        return {
            'sources': conservative_force,
            'target': safe_target,
            'type': 'defensive_consolidation'
        }
    
    def _opportunistic_strike(self, available_towers: List[Tower], targets: List[Tower]) -> Optional[dict]:
        """Strike cơ hội với single attack - always return an action"""
        if not targets or not available_towers:
            print("_opportunistic_strike: No targets or available towers")
            return None
        
        print(f"_opportunistic_strike: {len(available_towers)} towers, {len(targets)} targets")
        
        # Always try to find a viable action - lower requirements
        for source_tower in available_towers:
            if source_tower.troops > 0:  # Chỉ cần > 0 thay vì > 1
                # Find closest target
                closest_target = min(targets, key=lambda t: source_tower.distance_to(t))
                
                print(f"_opportunistic_strike: Found action - {source_tower.troops} troops attacking")
                return {
                    'source': source_tower,
                    'target': closest_target,
                    'type': 'single_attack'
                }
        
        print("_opportunistic_strike: No viable action found")
        return None
    
    def _select_assault_target(self, targets: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn target cho coordinated assault"""
        def assault_priority(target):
            # Ưu tiên player towers
            owner_bonus = 3.0 if target.owner == OwnerType.PLAYER else 1.0
            
            # Ưu tiên targets có nhiều support nearby
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 250 and t.troops > 5)
            support_factor = nearby_support * 0.6
            
            # Factor in troop count (prefer weaker targets)
            troops_factor = 1.0 / max(target.troops, 1)
            
            return owner_bonus + support_factor + troops_factor
        
        return max(targets, key=assault_priority)
    
    def _assemble_assault_force(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tập hợp force cho assault - Simple logic for all difficulties"""
        potential_attackers = []
        
        # Simple parameters for all difficulties
        max_distance = 300
        max_attackers_count = 2
        
        for tower in available_towers:
            distance = tower.distance_to(target)
            if distance < max_distance and tower.troops > 1:
                # Simple priority calculation
                priority = tower.troops + (200 / max(distance, 1))
                potential_attackers.append((tower, priority))
        
        # Sort and select best attackers
        potential_attackers.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(max_attackers_count, len(potential_attackers))
        
        if not potential_attackers and available_towers:
            return [available_towers[0]]
        
        return [tower for tower, _ in potential_attackers[:selected_count]]
    
    def _select_expansion_target(self, neutral_targets: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn target cho expansion"""
        def expansion_value(target):
            # Ưu tiên targets dễ chiếm
            ease_factor = 1.0 / max(target.troops, 1)
            
            # Ưu tiên vị trí strategic
            center_distance = math.sqrt((target.x - 400)**2 + (target.y - 300)**2)
            position_factor = 1.0 / max(center_distance, 1) * 200
            
            # Support availability
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 280)
            support_factor = nearby_support * 0.3
            
            return ease_factor + position_factor + support_factor
        
        return max(neutral_targets, key=expansion_value)
    
    def _assemble_expansion_force(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tập hợp force cho expansion - Enhanced for better multi-tower coordination"""
        expanders = []
        
        # Enhanced coordination parameters by difficulty
        if self.difficulty == "easy":
            max_distance = 300
            max_expanders_count = 2
        elif self.difficulty == "medium":
            max_distance = 350  # Longer range
            max_expanders_count = 3  # More towers
        else:  # hard
            max_distance = 400  # Maximum range
            max_expanders_count = 4  # Maximum coordination
        
        print(f"_assemble_expansion_force: {len(available_towers)} available towers, target at ({target.x}, {target.y})")
        
        for tower in available_towers:
            distance = tower.distance_to(target)
            if distance < max_distance and tower.troops > 0:
                # Enhanced value calculation
                troops_value = tower.troops * 0.4
                distance_value = (1.0 / max(distance, 1)) * 100
                # Difficulty bonus for better coordination
                difficulty_bonus = {"easy": 0, "medium": 15, "hard": 30}[self.difficulty]
                
                value = troops_value + distance_value + difficulty_bonus
                expanders.append((tower, value))
                print(f"  Added tower at ({tower.x}, {tower.y}) with {tower.troops} troops, distance={distance:.1f}, value={value:.1f}")
        
        expanders.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(max_expanders_count, len(expanders))
        
        # Ensure at least 1 tower if available
        if not expanders and available_towers:
            print("_assemble_expansion_force: No expanders, using fallback")
            return [available_towers[0]]
        
        # For medium/hard, prefer multiple towers for expansion
        if self.difficulty in ["medium", "hard"] and len(expanders) >= 2:
            selected_count = max(2, selected_count)  # At least 2 towers
        
        # Remove duplicates and ensure unique towers
        selected_towers = []
        seen_positions = set()
        
        for tower, _ in expanders[:selected_count]:
            tower_pos = (tower.x, tower.y)
            if tower_pos not in seen_positions:
                selected_towers.append(tower)
                seen_positions.add(tower_pos)
                print(f"  Selected tower at ({tower.x}, {tower.y}) with {tower.troops} troops for expansion")
        
        print(f"_assemble_expansion_force: Selected {len(selected_towers)} unique towers for expansion")
        return selected_towers
    
    def _select_safe_target(self, targets: List[Tower], available_towers: List[Tower]) -> Tower:
        """Chọn target an toàn cho defensive action"""
        def safety_score(target):
            # Ưu tiên targets yếu
            weakness_factor = 1.0 / max(target.troops, 1)
            
            # Ưu tiên targets có support gần
            nearby_support = sum(1 for t in available_towers 
                               if t.distance_to(target) < 200)
            support_factor = nearby_support * 0.4
            
            return weakness_factor + support_factor
        
        return max(targets, key=safety_score)
    
    def _assemble_conservative_force(self, available_towers: List[Tower], target: Tower) -> List[Tower]:
        """Tập hợp conservative force - Enhanced for multi-tower coordination"""
        conservative = []
        
        # Enhanced parameters by difficulty
        if self.difficulty == "easy":
            max_distance = 220
            max_conservative_count = 1
        elif self.difficulty == "medium":
            max_distance = 270  # Longer range for medium
            max_conservative_count = 2  # Allow 2 towers
        else:  # hard
            max_distance = 320  # Even longer range for hard
            max_conservative_count = 3  # Allow up to 3 towers
        
        # Collect potential conservative attackers
        for tower in available_towers:
            distance = tower.distance_to(target)
            if distance < max_distance and tower.troops > 0:
                conservative.append((tower, tower.troops + (1.0 / max(distance, 1)) * 50))
        
        # Sort by value and select best ones
        conservative.sort(key=lambda x: x[1], reverse=True)
        selected_count = min(max_conservative_count, len(conservative))
        
        # Return selected towers
        if conservative:
            return [tower for tower, _ in conservative[:selected_count]]
        elif available_towers:
            # Fallback: at least 1 tower
            return available_towers[:1]
        else:
            return []
    
    def _find_best_opportunity(self, available_towers: List[Tower], targets: List[Tower]) -> Optional[dict]:
        """Tìm opportunity tốt nhất cho single strike"""
        best_opportunity = None
        best_score = 0
        
        for source in available_towers:
            if source.troops <= 2:
                continue
                
            for target in targets:
                distance = source.distance_to(target)
                if distance > 300:
                    continue
                
                # Tính opportunity score
                troops_advantage = source.troops - target.troops
                distance_factor = 1.0 / max(distance, 1) * 100
                
                score = troops_advantage + distance_factor
                
                if score > best_score:
                    best_score = score
                    best_opportunity = {'source': source, 'target': target}
        
        return best_opportunity
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
        """Factory method để tạo AI strategy - SmartStrategy for all levels with different intensities"""
        strategies = {
            'easy': SmartStrategy(difficulty),      # Level 1 - Normal smart strategy
            'medium': SmartStrategy(difficulty),    # Level 2 - Enhanced smart strategy  
            'hard': SmartStrategy(difficulty),      # Level 3 - Advanced smart strategy
            'nightmare': AggressiveStrategy()       # Keep nightmare for special cases
        }
        return strategies.get(difficulty, SmartStrategy(difficulty))
    
    def set_difficulty(self, difficulty: str):
        """Thay đổi độ khó AI với advanced settings"""
        self.difficulty = difficulty
        self.strategy = self._create_strategy(difficulty)
        
        # Update strategy difficulty if it's SmartStrategy
        if hasattr(self.strategy, 'difficulty'):
            self.strategy.difficulty = difficulty
        
        # Adjust action interval and aggressiveness based on difficulty - Rollback to original simple settings
        difficulty_settings = {
            'easy': {
                'interval': 1500,     # 1.5 seconds for all levels
                'min_troops': 2,      # Simple requirements  
                'coordination': 0.2   # Low coordination
            },
            'medium': {
                'interval': 1500,     # Same as level 1
                'min_troops': 2,      # Same requirements
                'coordination': 0.2   # Same coordination
            },
            'hard': {
                'interval': 1500,     # Same as level 1  
                'min_troops': 2,      # Same requirements
                'coordination': 0.2   # Same coordination
            }
        }
        
        settings = difficulty_settings.get(difficulty, difficulty_settings['medium'])
        self.action_interval = settings['interval']
        self.min_troops_threshold = settings['min_troops']
        self.coordination_chance = settings['coordination']
    
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
    
    def execute_action(self, towers: List[Tower]) -> Optional[dict]:
        """
        Thực hiện hành động AI với multi-tower coordination
        Returns: dict với action info nếu có action được thực hiện
        """
        current_time = pygame.time.get_ticks()
        should_act = self.should_take_action()
        print(f"AI execute_action: should_act={should_act}, last_action={self.last_action_time}, current={current_time}, interval={self.action_interval}")
        
        if not should_act:
            return None
        
        enemy_towers = [t for t in towers if t.owner == OwnerType.ENEMY]
        print(f"AI execute_action: {len(enemy_towers)} enemy towers total")
        
        if not enemy_towers:
            print("AI execute_action: No enemy towers found")
            return None
        
        # Sử dụng strategy để quyết định action
        action = self.strategy.decide_action(enemy_towers, towers)
        
        # Debug: check if AI has action
        if not action:
            print(f"AI No Action: {len(enemy_towers)} enemy towers available")
            # Fallback: force một action đơn giản nếu có towers
            if enemy_towers:
                print(f"AI Fallback: Trying to create fallback action")
                all_targets = [t for t in towers if t.owner != OwnerType.ENEMY]
                print(f"AI Fallback: Found {len(all_targets)} targets")
                if all_targets and enemy_towers[0].troops > 0:
                    print(f"AI Fallback: Creating action with tower troops={enemy_towers[0].troops}")
                    action = {
                        'source': enemy_towers[0],
                        'target': all_targets[0],
                        'type': 'single_attack'
                    }
                    print(f"AI Fallback action created successfully")
        
        if not action:
            return None
        
        print(f"AI Action type: {action.get('type', 'unknown')}")  # Debug
        
        if action:
            # Handle both single and multi-tower actions
            if 'sources' in action:  # Multi-tower action
                sources = action['sources']
                target = action['target']
                action_type = action.get('type', 'multi_attack')
                
                successful_attacks = []
                total_troops = 0
                
                print(f"AI Multi-action debug: sources={len(sources)}, target exists={target is not None}")
                print(f"AI Multi-action: Target at ({target.x}, {target.y}) with {target.troops} troops")
                
                # Debug: Check for duplicate towers
                source_positions = [(tower.x, tower.y) for tower in sources]
                unique_positions = set(source_positions)
                print(f"AI Multi-action: {len(sources)} source towers, {len(unique_positions)} unique positions")
                if len(sources) != len(unique_positions):
                    print("WARNING: Duplicate towers detected in sources!")
                
                for i, source_tower in enumerate(sources):
                    print(f"  Source {i}: Tower at ({source_tower.x}, {source_tower.y}) with {source_tower.troops} troops, can_send={source_tower.can_send_troops()}")
                
                for i, source_tower in enumerate(sources):
                    if source_tower.can_send_troops():
                        print(f"AI Multi-action {i}: Sending troops from tower at ({source_tower.x}, {source_tower.y}) with {source_tower.troops} troops")
                        troops_count = source_tower.send_troops(target)
                        print(f"AI Multi-action {i}: Sent {troops_count} troops")
                        if troops_count > 0:
                            successful_attacks.append({
                                'source': source_tower,
                                'target': target,
                                'troops_count': troops_count
                            })
                            total_troops += troops_count
                    else:
                        print(f"AI Multi-action {i}: Tower at ({source_tower.x}, {source_tower.y}) cannot send troops")
                
                if successful_attacks:
                    self.actions_taken += 1
                    self.last_action_time = pygame.time.get_ticks()
                    
                    # Không thêm stagger delay để AI có thể hành động liên tục
                    # base_delay = random.randint(200, 500)
                    # for i, attack in enumerate(successful_attacks):
                    #     additional_delay = base_delay + (i * 100)  # 100ms between each attack
                    #     self.last_action_time += additional_delay
                    
                    return {
                        'attacks': successful_attacks,
                        'target': target,
                        'total_troops': total_troops,
                        'action_type': action_type
                    }
            
            else:  # Legacy single-tower action
                source_tower = action.get('source')
                target_tower = action.get('target')
                
                print(f"AI single action: source troops={source_tower.troops if source_tower else 'None'}, can_send={source_tower.can_send_troops() if source_tower else 'None'}")
                
                if source_tower and target_tower:
                    print(f"AI debug: source_tower exists, target_tower exists")
                    print(f"AI debug: source troops={source_tower.troops}, owner={source_tower.owner}")
                    
                    if source_tower.can_send_troops():
                        print(f"AI debug: can_send_troops=True, calling send_troops()")
                        troops_count = source_tower.send_troops(target_tower)
                        print(f"AI sent {troops_count} troops from tower")
                        
                        if troops_count > 0:
                            self.actions_taken += 1
                            self.last_action_time = pygame.time.get_ticks()
                            
                            # Không thêm additional_delay để AI có thể hành động liên tục
                            # additional_delay = random.randint(300, 900)
                            # self.last_action_time += additional_delay
                            
                            return {
                                'source': source_tower,
                                'target': target_tower,
                                'troops_count': troops_count,
                            'action_type': 'single_attack'
                        }
        
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
