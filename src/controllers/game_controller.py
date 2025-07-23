"""
Game Controller - Main game logic và state management
Thể hiện Singleton Pattern, Observer Pattern, và State Pattern
"""
import pygame
import random
from typing import List, Optional, Tuple
from ..models.base import Observer, Subject
from ..models.tower import Tower, PlayerTower, EnemyTower
from ..models.troop import Troop, PlayerTroop, EnemyTroop
from ..controllers.ai_controller import AIController
from ..utils.constants import OwnerType, GameState, GameSettings

class GameController(Subject, Observer):
    """
    Singleton Game Controller class
    Quản lý toàn bộ game logic và state
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(GameController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        
        # Game state
        self._game_state = GameState.PLAYING
        self._towers: List[Tower] = []
        self._troops: List[Troop] = []
        self._selected_tower: Optional[Tower] = None
        self._winner: Optional[str] = None
        
        # Controllers
        self._ai_controller = AIController('medium')
        self._ai_controller.attach(self)  # Observer pattern
        
        # Game statistics
        self._game_start_time = pygame.time.get_ticks()
        self._player_actions = 0
        self._total_battles = 0
        
        # Initialize game
        self._create_initial_towers()
        self._setup_observers()
        
        self._initialized = True
    
    def _setup_observers(self):
        """Setup observer relationships"""
        for tower in self._towers:
            tower.attach(self)  # Game controller observes all towers
    
    def _create_initial_towers(self):
        """Tạo towers ban đầu theo design pattern"""
        # Sử dụng Factory pattern concept
        tower_factory = TowerFactory()
        
        # Player towers (moved down to avoid HUD overlap)
        player_positions = [(150, 200), (150, 600)]
        for x, y in player_positions:
            tower = tower_factory.create_player_tower(x, y)
            self._towers.append(tower)
        
        # Enemy towers
        enemy_positions = [(850, 200), (850, 600)]
        for x, y in enemy_positions:
            tower = tower_factory.create_enemy_tower(x, y)
            self._towers.append(tower)
        
        # Neutral towers (adjusted positions)
        neutral_positions = [
            (500, 150), (200, 400), (800, 400),
            (500, 350), (400, 600), (600, 600)
        ]
        for x, y in neutral_positions:
            tower = tower_factory.create_neutral_tower(x, y)
            self._towers.append(tower)
    
    @property
    def game_state(self) -> str:
        """Getter cho game state"""
        return self._game_state
    
    @property
    def towers(self) -> List[Tower]:
        """Getter cho towers list"""
        return self._towers.copy()  # Return copy để protect encapsulation
    
    @property
    def troops(self) -> List[Troop]:
        """Getter cho troops list"""
        return self._troops.copy()  # Return copy để protect encapsulation
    
    @property
    def selected_tower(self) -> Optional[Tower]:
        """Getter cho selected tower"""
        return self._selected_tower
    
    @property
    def winner(self) -> Optional[str]:
        """Getter cho winner"""
        return self._winner
    
    def update_observer(self, event_type: str, data: dict):
        """
        Implementation của Observer interface
        Xử lý events từ towers và other objects
        """
        if event_type == "tower_clicked":
            self._handle_tower_click(data['tower'], data['position'])
        
        elif event_type == "troops_sent":
            self._handle_troops_sent(data)
        
        elif event_type == "owner_changed":
            self._handle_tower_captured(data)
            self._check_win_condition()
        
        elif event_type == "troops_changed":
            # Could be used for UI updates or statistics
            pass
        
        elif event_type == "ai_action_taken":
            # Log AI actions for debugging
            if hasattr(self, '_debug_mode') and self._debug_mode:
                print(f"AI {data.get('strategy', 'Unknown')} sent {data.get('troops_count', 0)} troops")
    
    def _handle_tower_click(self, tower: Tower, position: Tuple[float, float]):
        """Xử lý click vào tower"""
        if self._game_state != GameState.PLAYING:
            return
        
        if self._selected_tower is None:
            # Chọn tower nếu là player tower và có quân
            if tower.owner == OwnerType.PLAYER and tower.can_send_troops():
                self._selected_tower = tower
                tower.selected = True
                self._player_actions += 1
        else:
            # Gửi quân nếu click vào tower khác
            if tower != self._selected_tower:
                self._send_troops(self._selected_tower, tower)
            
            # Deselect tower
            self._deselect_tower()
    
    def _send_troops(self, source: Tower, target: Tower):
        """Gửi quân từ source đến target"""
        if source.owner != OwnerType.PLAYER:
            return
        
        troops_count = source.send_troops(target)
        if troops_count > 0:
            # Tạo player troop
            troop = PlayerTroop(
                source.x, source.y,
                target.x, target.y,
                troops_count
            )
            self._troops.append(troop)
            
            # Notify observers
            self.notify("troops_created", {
                "troop": troop,
                "source": source,
                "target": target
            })
    
    def _handle_troops_sent(self, data: dict):
        """Xử lý event troops được gửi"""
        self._total_battles += 1
    
    def _handle_tower_captured(self, data: dict):
        """Xử lý event tower bị chiếm"""
        tower = data['tower']
        old_owner = data['old_owner']
        new_owner = data['new_owner']
        
        # Notify observers about tower capture
        self.notify("tower_captured", {
            "tower": tower,
            "old_owner": old_owner,
            "new_owner": new_owner
        })
    
    def handle_click(self, position: Tuple[float, float]):
        """
        Public method để xử lý click từ UI
        """
        x, y = position
        
        # Tìm tower được click
        clicked_tower = None
        for tower in self._towers:
            if tower.contains_point(x, y):
                clicked_tower = tower
                break
        
        if clicked_tower:
            clicked_tower.on_click(position)
        else:
            # Click vào empty space, deselect
            self._deselect_tower()
    
    def _deselect_tower(self):
        """Deselect current tower"""
        if self._selected_tower:
            self._selected_tower.selected = False
            self._selected_tower = None
    
    def update(self, dt: float):
        """
        Main update method cho game logic
        """
        if self._game_state != GameState.PLAYING:
            return
        
        # Update towers
        for tower in self._towers:
            tower.update(dt)
        
        # Update troops và handle arrivals
        self._update_troops(dt)
        
        # AI actions
        ai_troop = self._ai_controller.execute_action(self._towers)
        if ai_troop:
            self._troops.append(ai_troop)
            target_x, target_y = ai_troop.target_position
            print(f"AI Action: Enemy tấn công từ ({ai_troop.x:.0f}, {ai_troop.y:.0f}) đến ({target_x:.0f}, {target_y:.0f}) với {ai_troop.count} quân")
        
        # Check win condition
        self._check_win_condition()
    
    def _update_troops(self, dt: float):
        """Update troops và xử lý combat + khi troops đến đích"""
        troops_to_remove = []
        
        # Update all troops
        for troop in self._troops:
            troop.update(dt)
        
        # Check for troop-to-troop combat
        self._handle_troop_combat()
        
        # Check for troops reaching destinations
        for i, troop in enumerate(self._troops):
            if troop.has_reached_target():
                target_tower = self._find_target_tower(troop)
                if target_tower:
                    # Xử lý combat với tower
                    was_captured = target_tower.receive_attack(troop.count, troop.owner)
                    if was_captured:
                        self.notify("tower_captured", {
                            "tower": target_tower,
                            "old_owner": target_tower.owner,
                            "new_owner": troop.owner
                        })
                
                troops_to_remove.append(i)
        
        # Remove arrived troops
        for i in reversed(troops_to_remove):
            del self._troops[i]
    
    def _handle_troop_combat(self):
        """Xử lý combat giữa các troops"""
        troops_to_remove = []
        
        for i in range(len(self._troops)):
            if i in troops_to_remove:
                continue
                
            troop1 = self._troops[i]
            
            for j in range(i + 1, len(self._troops)):
                if j in troops_to_remove:
                    continue
                    
                troop2 = self._troops[j]
                
                # Kiểm tra collision giữa troops khác owner
                if troop1.is_colliding_with(troop2):
                    print(f"Combat: {troop1.owner} ({troop1.count}) vs {troop2.owner} ({troop2.count})")
                    
                    # Thực hiện combat
                    winner1, winner2 = troop1.combat_with(troop2)
                    
                    # Xử lý kết quả combat
                    if winner1 is None:
                        troops_to_remove.append(i)
                    if winner2 is None:
                        troops_to_remove.append(j)
                    
                    # Chỉ xử lý một combat per troop per update
                    break
        
        # Remove defeated troops
        for i in reversed(sorted(troops_to_remove)):
            if i < len(self._troops):
                del self._troops[i]
    
    def _find_target_tower(self, troop: Troop) -> Optional[Tower]:
        """Tìm tower target của troop"""
        target_x, target_y = troop.target_position
        
        for tower in self._towers:
            distance = ((tower.x - target_x)**2 + (tower.y - target_y)**2)**0.5
            if distance <= tower.radius:
                return tower
        return None
    
    def _check_win_condition(self):
        """Kiểm tra điều kiện thắng thua - Player vs Enemy (không quan tâm neutral)"""
        # Đếm towers theo owner
        owner_count = {}
        for tower in self._towers:
            owner = tower.owner
            owner_count[owner] = owner_count.get(owner, 0) + 1
        
        print(f"Tower owners: {owner_count}")
        
        player_towers = owner_count.get(OwnerType.PLAYER, 0)
        enemy_towers = owner_count.get(OwnerType.ENEMY, 0)
        
        # Kiểm tra win condition: một bên không còn tower nào
        winner = None
        if player_towers > 0 and enemy_towers == 0:
            winner = OwnerType.PLAYER
        elif enemy_towers > 0 and player_towers == 0:
            winner = OwnerType.ENEMY
        
        if winner:
            self._game_state = GameState.GAME_OVER
            self._winner = winner
            
            print(f"Game Over! Winner: {self._winner}")
            
            # Notify về state change trước
            self.notify("game_state_changed", {
                "old_state": GameState.PLAYING,
                "new_state": GameState.GAME_OVER
            })
            
            # Notify observers về game over
            self.notify("game_over", {
                "winner": self._winner,
                "game_duration": pygame.time.get_ticks() - self._game_start_time,
                "player_actions": self._player_actions,
                "total_battles": self._total_battles
            })
    
    def restart_game(self):
        """Restart game"""
        # Reset state
        self._game_state = GameState.PLAYING
        self._towers.clear()
        self._troops.clear()
        self._selected_tower = None
        self._winner = None
        
        # Reset statistics
        self._game_start_time = pygame.time.get_ticks()
        self._player_actions = 0
        self._total_battles = 0
        
        # Recreate game objects
        self._create_initial_towers()
        self._setup_observers()
        
        # Reset AI
        self._ai_controller.reset_stats()
        
        # Notify observers
        self.notify("game_restarted", {})
    
    def pause_game(self):
        """Pause/unpause game"""
        if self._game_state == GameState.PLAYING:
            self._game_state = GameState.PAUSED
        elif self._game_state == GameState.PAUSED:
            self._game_state = GameState.PLAYING
    
    def get_game_stats(self) -> dict:
        """Lấy thống kê game"""
        current_time = pygame.time.get_ticks()
        duration = current_time - self._game_start_time
        
        player_towers = len([t for t in self._towers if t.owner == OwnerType.PLAYER])
        enemy_towers = len([t for t in self._towers if t.owner == OwnerType.ENEMY])
        neutral_towers = len([t for t in self._towers if t.owner == OwnerType.NEUTRAL])
        
        return {
            "game_duration": duration,
            "player_actions": self._player_actions,
            "total_battles": self._total_battles,
            "player_towers": player_towers,
            "enemy_towers": enemy_towers,
            "neutral_towers": neutral_towers,
            "active_troops": len(self._troops),
            "ai_stats": self._ai_controller.get_performance_stats()
        }
    
    def set_ai_difficulty(self, difficulty: str):
        """Thay đổi độ khó AI"""
        self._ai_controller.set_difficulty(difficulty)
    
    def __str__(self) -> str:
        """String representation của game controller"""
        stats = self.get_game_stats()
        return (f"GameController(state={self._game_state}, "
                f"towers={len(self._towers)}, troops={len(self._troops)}, "
                f"actions={stats['player_actions']})")

class TowerFactory:
    """
    Factory class để tạo towers
    Thể hiện Factory Pattern
    """
    
    @staticmethod
    def create_player_tower(x: float, y: float) -> PlayerTower:
        """Tạo player tower với 10 quân ban đầu"""
        return PlayerTower(x, y, troops=10)
    
    @staticmethod
    def create_enemy_tower(x: float, y: float) -> EnemyTower:
        """Tạo enemy tower với 1 quân ban đầu"""
        return EnemyTower(x, y, troops=1)
    
    @staticmethod
    def create_neutral_tower(x: float, y: float) -> Tower:
        """Tạo neutral tower"""
        troops = random.randint(5, 15)  # Giảm một chút cho cân bằng
        return Tower(x, y, OwnerType.NEUTRAL, troops)
