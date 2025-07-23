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
from ..controllers.level_manager import LevelManager
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
        self._game_ended = False  # Flag để tránh check win condition nhiều lần
        
        # Level management
        self._level_manager = LevelManager()
        
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
        
        # Player towers (left side - farther from center)
        player_positions = [(100, 200), (100, 600)]
        for x, y in player_positions:
            tower = tower_factory.create_player_tower(x, y)
            self._towers.append(tower)
        
        # Enemy towers (right side - farther from center)
        enemy_positions = [(900, 200), (900, 600)]
        for x, y in enemy_positions:
            tower = tower_factory.create_enemy_tower(x, y)
            self._towers.append(tower)
        
        # Neutral towers (centered between players)
        neutral_positions = [
            (500, 150), (250, 400), (750, 400),
            (500, 350), (350, 600), (650, 600)
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
    
    @property
    def level_manager(self) -> LevelManager:
        """Getter cho level manager"""
        return self._level_manager
    
    def get_current_level_info(self) -> str:
        """Lấy thông tin level hiện tại"""
        return self._level_manager.get_level_info()
    
    def get_level_progress(self) -> str:
        """Lấy tiến độ level"""
        return self._level_manager.get_progress()
    
    def advance_to_next_level(self):
        """Chuyển sang level tiếp theo"""
        if self._level_manager.complete_current_level():
            # Nếu có level tiếp theo, bắt đầu level mới
            self._init_new_level()
            self._game_state = GameState.PLAYING
            # Thông báo cho observer về level mới
            self.notify("level_changed", {
                "level": self._level_manager.current_level,
                "level_info": self._level_manager.get_level_info()
            })
        else:
            # Đã hoàn thành tất cả level
            self._game_state = GameState.GAME_OVER
            self.notify("all_levels_complete", {})
    
    def handle_level_complete_input(self, key):
        """Xử lý input khi ở trạng thái level complete"""
        if self._game_state == GameState.LEVEL_COMPLETE:
            if key == pygame.K_SPACE:
                # Continue to next level
                self._init_new_level()
                self._game_state = GameState.PLAYING
                # Hide level complete dialog
                self.notify("level_started", {
                    "level": self._level_manager.current_level,
                    "level_info": self._level_manager.get_level_info()
                })
            elif key == pygame.K_r:
                # Restart from level 1
                self.restart_game()
    
    def _init_new_level(self):
        """Khởi tạo level mới"""
        level_config = self._level_manager.get_current_level_config()
        print(f"Initializing {level_config['name']}...")
        
        # Reset game objects
        self._towers.clear()
        self._troops.clear()
        self._selected_tower = None
        self._winner = None
        
        # Reset statistics cho level mới
        self._game_start_time = pygame.time.get_ticks()
        self._player_actions = 0
        self._total_battles = 0
        
        # Setup AI theo level
        self._ai_controller.set_difficulty(level_config['ai_difficulty'])
        
        # Tạo towers cho level mới
        self._create_initial_towers_for_level(level_config)
        self._setup_observers()
        
        # Reset AI
        self._ai_controller.reset_stats()
        
        # Notify observers về level mới
        self.notify("towers_updated", {"towers": self._towers})
        self.notify("troops_updated", {"troops": self._troops})
        
        print(f"Level {self._level_manager.current_level} initialized successfully")
    
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
        # Nếu game đã kết thúc thì không check nữa
        if self._game_ended or self._game_state in [GameState.GAME_OVER, GameState.LEVEL_COMPLETE]:
            return
            
        # Đếm towers theo owner
        owner_count = {}
        for tower in self._towers:
            owner = tower.owner
            owner_count[owner] = owner_count.get(owner, 0) + 1
        
        print(f"Tower owners: {owner_count}")
        
        player_towers = owner_count.get(OwnerType.PLAYER, 0)
        enemy_towers = owner_count.get(OwnerType.ENEMY, 0)
        
        print(f"Player towers: {player_towers}, Enemy towers: {enemy_towers}")
        
        # Kiểm tra win condition: một bên không còn tower nào
        winner = None
        if player_towers > 0 and enemy_towers == 0:
            winner = OwnerType.PLAYER
        elif enemy_towers > 0 and player_towers == 0:
            winner = OwnerType.ENEMY
        
        if winner:
            self._game_ended = True  # Đánh dấu game đã kết thúc
            print(f"WIN CONDITION MET! Winner: {winner}")
            old_state = self._game_state
            
            # Xử lý level progression
            if winner == OwnerType.PLAYER:
                # Player thắng - kiểm tra có level tiếp theo không
                has_next_level = self._level_manager.complete_current_level()
                completed_level = self._level_manager.current_level
                
                self._game_state = GameState.LEVEL_COMPLETE
                self.notify("level_complete", {
                    "winner": winner,
                    "level": completed_level,  # Level vừa hoàn thành
                    "has_next_level": has_next_level
                })
            else:
                # Player thua
                self._level_manager.reset_to_level_1()
                self._game_state = GameState.GAME_OVER
                
                # Chỉ notify game_over khi player thua
                self.notify("game_over", {
                    "winner": winner,
                    "game_duration": pygame.time.get_ticks() - self._game_start_time,
                    "player_actions": self._player_actions,
                    "total_battles": self._total_battles,
                    "level": self._level_manager.current_level,
                    "level_info": self._level_manager.get_level_info()
                })
            
            self._winner = winner
            
            print(f"Game state changed: {old_state} -> {self._game_state}")
            
            # Notify về state change
            self.notify("game_state_changed", {
                "old_state": old_state,
                "new_state": self._game_state
            })
            
            print(f"Notifications sent - winner: {self._winner}")
        else:
            print("No winner yet, game continues")
    
    def restart_game(self):
        """Restart game với level config hiện tại"""
        level_config = self._level_manager.get_current_level_config()
        print(f"Starting {level_config['name']}...")
        
        # Reset state
        old_state = self._game_state
        self._game_state = GameState.PLAYING
        self._towers.clear()
        self._troops.clear()
        self._selected_tower = None
        self._winner = None
        self._game_ended = False  # Reset flag
        
        # Reset statistics
        self._game_start_time = pygame.time.get_ticks()
        self._player_actions = 0
        self._total_battles = 0
        
        # Setup AI theo level
        self._ai_controller.set_difficulty(level_config['ai_difficulty'])
        
        # Recreate game objects theo level config
        self._create_initial_towers_for_level(level_config)
        self._setup_observers()
        
        # Reset AI
        self._ai_controller.reset_stats()
        
        # Notify observers về state change nếu cần
        if old_state != GameState.PLAYING:
            self.notify("game_state_changed", {
                "old_state": old_state,
                "new_state": GameState.PLAYING
            })
        
        # Notify observers về restart
        self.notify("game_restarted", {
            "level": self._level_manager.current_level,
            "level_info": level_config['name']
        })
        self.notify("towers_updated", {"towers": self._towers})
        self.notify("troops_updated", {"troops": self._troops})
        
        # Ẩn pause menu nếu đang hiển thị
        self.notify("game_resumed", {})
        
        print("Game restarted successfully")
    
    def _create_initial_towers_for_level(self, level_config: dict):
        """Tạo towers ban đầu theo config của level"""
        import random
        
        # Vị trí cố định cho player và enemy towers để tránh gần nhau
        player_positions = [(100, 200), (100, 500), (120, 350)]
        enemy_positions = [(900, 200), (900, 500), (880, 350)]
        neutral_positions = [
            (500, 150), (500, 450), (500, 600),
            (350, 300), (650, 300), (400, 550), (600, 550)
        ]
        
        # Tạo player towers
        for i in range(level_config['player_towers']):
            if i < len(player_positions):
                x, y = player_positions[i]
                tower = PlayerTower(x, y, level_config['initial_troops'])
                self._towers.append(tower)
        
        # Tạo enemy towers
        for i in range(level_config['enemy_towers']):
            if i < len(enemy_positions):
                x, y = enemy_positions[i]
                enemy_troops = level_config.get('enemy_initial_troops', level_config['initial_troops'])
                tower = EnemyTower(x, y, enemy_troops)
                self._towers.append(tower)
                
        # Tạo neutral towers
        random.shuffle(neutral_positions)  # Chỉ shuffle neutral positions
        for i in range(level_config['neutral_towers']):
            if i < len(neutral_positions):
                x, y = neutral_positions[i]
                tower = Tower(x, y, OwnerType.NEUTRAL, level_config['initial_troops'])
                self._towers.append(tower)
        
        enemy_troops = level_config.get('enemy_initial_troops', level_config['initial_troops'])
        player_troops = level_config['initial_troops']
        print(f"Created level: {level_config['player_towers']} player towers ({player_troops} troops each), "
              f"{level_config['enemy_towers']} enemy towers ({enemy_troops} troops each), "
              f"{level_config['neutral_towers']} neutral towers")
    
    def pause_game(self):
        """Pause/unpause game"""
        old_state = self._game_state
        
        if self._game_state == GameState.PLAYING:
            self._game_state = GameState.PAUSED
            print("Game paused")
        elif self._game_state == GameState.PAUSED:
            self._game_state = GameState.PLAYING
            print("Game resumed")
        
        # Notify observers về state change
        self.notify("game_state_changed", {
            "old_state": old_state,
            "new_state": self._game_state
        })
        
        # Emit specific events for pause menu
        if self._game_state == GameState.PAUSED:
            self.notify("game_paused", {})
        else:
            self.notify("game_resumed", {})
    
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
