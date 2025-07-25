"""
Game Controller - Main game logic và state management
Thể hiện Singleton Pattern, Observer Pattern, và State Pattern
"""
import pygame
import random
import math
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
        
        # Troop spawning system
        self._spawn_queue = []  # Queue of troops waiting to spawn
        
        # Initialize game
        self._create_initial_towers()
        self._setup_observers()
        
        self._initialized = True
    
    def _setup_observers(self):
        """Setup observer relationships"""
        for tower in self._towers:
            tower.attach(self)  # Game controller observes all towers
    
    def _create_initial_towers(self):
        """Tạo towers ban đầu theo design pattern với vị trí động"""
        # Calculate dynamic positions based on screen size
        positions = self._calculate_tower_positions()
        
        # Player towers (left side)
        for x, y in positions['player']:
            tower = PlayerTower(x, y, troops=10)
            self._towers.append(tower)
        
        # Enemy towers (right side)
        for x, y in positions['enemy']:
            tower = EnemyTower(x, y, troops=1)
            self._towers.append(tower)
        
        # Neutral towers (scattered between)
        import random
        for x, y in positions['neutral']:
            troops = random.randint(5, 15)
            tower = Tower(x, y, OwnerType.NEUTRAL, troops)
            self._towers.append(tower)
    
    def _calculate_tower_positions(self):
        """Calculate tower positions based on current screen dimensions - truly responsive"""
        # Use base game dimensions (1024x576) as reference but make it more responsive
        base_width = 1024
        base_height = 576
        
        # Calculate margins and safe zones as percentages for better scaling
        margin_x_percent = 0.08  # 8% margin from edges
        margin_y_percent = 0.2   # 20% margin from top (for HUD)
        bottom_margin_percent = 0.08  # 8% margin from bottom
        
        # Calculate actual positions
        margin_x = base_width * margin_x_percent
        margin_y = base_height * margin_y_percent
        safe_bottom = base_height * (1 - bottom_margin_percent)
        available_height = safe_bottom - margin_y
        
        # Player side (far left)
        player_x = margin_x
        player_positions = [
            (player_x, margin_y + available_height * 0.25),  # Upper player tower
            (player_x, margin_y + available_height * 0.75)   # Lower player tower
        ]
        
        # Enemy side (far right)
        enemy_x = base_width - margin_x
        enemy_positions = [
            (enemy_x, margin_y + available_height * 0.25),   # Upper enemy tower
            (enemy_x, margin_y + available_height * 0.75)    # Lower enemy tower
        ]
        
        # Neutral towers (distributed in middle area for better gameplay)
        center_x = base_width * 0.5
        left_zone = base_width * 0.25
        right_zone = base_width * 0.75
        mid_left = base_width * 0.35
        mid_right = base_width * 0.65
        
        neutral_positions = [
            (center_x, margin_y + available_height * 0.1),     # Top center
            (left_zone, margin_y + available_height * 0.4),    # Left middle
            (right_zone, margin_y + available_height * 0.4),   # Right middle
            (center_x, margin_y + available_height * 0.6),     # Center lower
            (mid_left, margin_y + available_height * 0.85),    # Lower left
            (mid_right, margin_y + available_height * 0.85)    # Lower right
        ]
        
        return {
            'player': player_positions,
            'enemy': enemy_positions,
            'neutral': neutral_positions
        }
    
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
        self._spawn_queue.clear()  # Clear spawn queue
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
        """Gửi quân từ source đến target với individual troops spawning gradually"""
        if source.owner != OwnerType.PLAYER:
            return
        
        troops_count = source.send_troops(target)
        if troops_count > 0:
            # Tạo spawn queue thay vì spawn tất cả cùng lúc
            self._create_troop_spawn_queue(
                source.x, source.y, 
                target.x, target.y,
                troops_count, 
                OwnerType.PLAYER
            )
            
            # Notify observers về troops creation
            self.notify("troops_spawn_started", {
                "count": troops_count,
                "source": source,
                "target": target
            })
    
    def _create_troop_spawn_queue(self, start_x: float, start_y: float, 
                                  target_x: float, target_y: float, 
                                  count: int, owner: str):
        """Tạo spawn queue để troops xuất hiện dần dần từ tower với timing đều và tránh conflicts"""
        if count <= 0:
            return
        
        # Tìm thời gian spawn cuối cùng từ cùng tower để tránh conflicts
        current_time = pygame.time.get_ticks()
        last_spawn_time = current_time
        
        # Kiểm tra spawn queue hiện tại để tìm spawn time cuối cùng từ tower này
        tower_entries = [entry for entry in self._spawn_queue 
                        if abs(entry['x'] - start_x) < 5 and abs(entry['y'] - start_y) < 5 
                        and entry['owner'] == owner]
        
        if tower_entries:
            # Tìm thời gian spawn cuối cùng từ tower này
            last_spawn_time = max(entry['spawn_time'] for entry in tower_entries)
            # Thêm buffer 50ms để tránh overlap
            last_spawn_time += 50
        
        # Tạo unique formation_id để nhóm troops cùng formation
        formation_id = f"{owner}_{start_x}_{start_y}_{target_x}_{target_y}_{current_time}"
        
        # Tạo spawn queue entries với timing không conflicts
        for i in range(count):
            # Fixed delay 120ms giữa mỗi troop để spacing rõ ràng hơn
            spawn_delay = i * 120  # 120ms = 0.12 giây delay để spacing rõ ràng
            
            spawn_entry = {
                'x': start_x,  # Spawn từ tower position
                'y': start_y,  # Spawn từ tower position
                'target_x': target_x,
                'target_y': target_y,
                'owner': owner,
                'spawn_time': last_spawn_time + spawn_delay,  # Dựa trên last_spawn_time
                'formation_id': formation_id,
                'formation_index': i  # Index trong formation
            }
            
            self._spawn_queue.append(spawn_entry)
            
        # Sort spawn queue theo thời gian để đảm bảo thứ tự đúng
        self._spawn_queue.sort(key=lambda x: x['spawn_time'])
            
        print(f"Created spawn queue for {count} {owner} troops with 120ms intervals, starting at {last_spawn_time}")

    
    def _process_spawn_queue(self):
        """Xử lý spawn queue để troops xuất hiện dần dần với timing chính xác"""
        if not self._spawn_queue:
            return
            
        current_time = pygame.time.get_ticks()
        spawned_count = 0
        
        # Xử lý tất cả entries đã đến thời gian spawn (có thể có lag)
        while self._spawn_queue and current_time >= self._spawn_queue[0]['spawn_time']:
            spawn_entry = self._spawn_queue[0]
            
            # Spawn troop trực tiếp từ tower đến target
            if spawn_entry['owner'] == OwnerType.PLAYER:
                troop = PlayerTroop(
                    spawn_entry['x'], spawn_entry['y'],  # Start at tower
                    spawn_entry['target_x'], spawn_entry['target_y'],   # Move directly to target
                    1  # Individual troop
                )
            else:
                troop = EnemyTroop(
                    spawn_entry['x'], spawn_entry['y'],  # Start at tower
                    spawn_entry['target_x'], spawn_entry['target_y'],   # Move directly to target
                    1  # Individual troop
                )
            
            troop._in_formation_phase = False
            troop._formation_id = spawn_entry['formation_id']
            
            # Thêm vào troops list
            self._troops.append(troop)
            
            # Xóa entry đã spawned
            self._spawn_queue.pop(0)
            spawned_count += 1
            
            # Notify observers về troop spawned
            self.notify("troop_spawned", {
                "troop": troop,
                "owner": spawn_entry['owner']
            })
            
            print(f"Spawned troop {spawn_entry['formation_index']} at time {current_time} (scheduled: {spawn_entry['spawn_time']})")
            
            # Giới hạn số troops spawn mỗi frame để tránh lag
            if spawned_count >= 3:
                break
        
        # Update troops list notification nếu có troops mới
        if spawned_count > 0:
            self.notify("troops_updated", {"troops": self._troops})
            print(f"Spawned {spawned_count} troops this frame, {len(self._spawn_queue)} remaining in queue")
    
    # Formation calculation removed - troops spawn directly to target now
    
    def _handle_troops_sent(self, data: dict):
        """Xử lý event troops được gửi"""
        self._total_battles += 1
    
    def _handle_tower_captured(self, data: dict):
        """Xử lý event tower bị chiếm"""
        tower = data['tower']
        old_owner = data['old_owner']
        new_owner = data['new_owner']
        
        # Play tower capture sound effect với volume thấp hơn để không đè lên các sound khác
        from ..utils.sound_manager import SoundManager
        sound_manager = SoundManager()
        sound_manager.play("tower_destroy", volume=0.6)  # Giảm từ 0.8 xuống 0.6
        
        # Notify observers about tower capture
        self.notify("tower_captured", {
            "tower": tower,
            "old_owner": old_owner,
            "new_owner": new_owner
        })
    
    def _notify_tower_captured(self, tower, old_owner, new_owner):
        """Helper method để notify tower capture với sound effect"""
        # Play tower capture sound effect với volume thấp hơn để không đè lên các sound khác
        from ..utils.sound_manager import SoundManager
        sound_manager = SoundManager()
        sound_manager.play("tower_destroy", volume=0.6)  # Giảm từ 0.8 xuống 0.6
        
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
        
        # Process spawn queue
        self._process_spawn_queue()
        
        # Update towers
        for tower in self._towers:
            tower.update(dt)
        
        # Update troops và handle arrivals
        self._update_troops(dt)
        
        # AI actions
        ai_action = self._ai_controller.execute_action(self._towers)
        if ai_action:
            # AI cũng sử dụng spawn queue system
            self._create_troop_spawn_queue(
                ai_action['source'].x, ai_action['source'].y,
                ai_action['target'].x, ai_action['target'].y,
                ai_action['troops_count'],
                OwnerType.ENEMY
            )
            print(f"AI Action: Enemy gửi {ai_action['troops_count']} quân từ ({ai_action['source'].x:.0f}, {ai_action['source'].y:.0f}) đến ({ai_action['target'].x:.0f}, {ai_action['target'].y:.0f})")
        
        # Check win condition
        self._check_win_condition()
    
    def _update_troops(self, dt: float):
        """Update troops và xử lý tower arrivals TRƯỚC combat để tránh troops bị destroy trước khi chạm tower"""
        troops_to_remove = []
        
        # Update all troops
        for troop in self._troops:
            troop.update(dt)
        
        # CRITICAL: Xử lý tower arrivals TRƯỚC combat để troops có cơ hội chạm tower
        # Group troops by target towers để xử lý simultaneous arrivals
        tower_arrivals = {}
        for i, troop in enumerate(self._troops):
            # Check if troop reached target
            if troop.has_reached_target():
                target_tower = self._find_target_tower(troop)
                if target_tower:
                    if target_tower not in tower_arrivals:
                        tower_arrivals[target_tower] = []
                    tower_arrivals[target_tower].append((i, troop))
        
        # Process each tower's arrivals
        for tower, arriving_troops in tower_arrivals.items():
            # Sort by owner to handle conflicts
            player_troops = [(i, t) for i, t in arriving_troops if t.owner == OwnerType.PLAYER]
            enemy_troops = [(i, t) for i, t in arriving_troops if t.owner == OwnerType.ENEMY]
            neutral_troops = [(i, t) for i, t in arriving_troops if t.owner == OwnerType.NEUTRAL]
            
            # Calculate total strengths
            total_player_strength = sum(t.count for _, t in player_troops)
            total_enemy_strength = sum(t.count for _, t in enemy_troops)
            total_neutral_strength = sum(t.count for _, t in neutral_troops)
            
            print(f"Tower at ({tower.x}, {tower.y}) - Owner: {tower.owner}, Troops: {tower.troops}")
            print(f"Arrivals - Player: {total_player_strength}, Enemy: {total_enemy_strength}, Neutral: {total_neutral_strength}")
            
            # Handle conflicts between player and enemy troops first
            if total_player_strength > 0 and total_enemy_strength > 0:
                print(f"Player vs Enemy conflict at tower")
                if total_player_strength > total_enemy_strength:
                    # Player wins
                    remaining_strength = total_player_strength - total_enemy_strength
                    print(f"Player wins with {remaining_strength} remaining troops")
                    if remaining_strength > 0:
                        old_owner = tower.owner  # Lưu owner cũ trước khi attack
                        was_captured = tower.receive_attack(remaining_strength, OwnerType.PLAYER)
                        if was_captured:
                            self._notify_tower_captured(tower, old_owner, OwnerType.PLAYER)
                elif total_enemy_strength > total_player_strength:
                    # Enemy wins
                    remaining_strength = total_enemy_strength - total_player_strength
                    print(f"Enemy wins with {remaining_strength} remaining troops")
                    if remaining_strength > 0:
                        old_owner = tower.owner  # Lưu owner cũ trước khi attack
                        was_captured = tower.receive_attack(remaining_strength, OwnerType.ENEMY)
                        if was_captured:
                            self._notify_tower_captured(tower, old_owner, OwnerType.ENEMY)
                else:
                    print(f"Equal strength - both sides cancel out")
                # Mark all conflicting troops for removal
                for i, _ in player_troops + enemy_troops:
                    if i not in troops_to_remove:
                        troops_to_remove.append(i)
            else:
                # No player vs enemy conflict - process each owner group separately
                if total_player_strength > 0:
                    print(f"Player attacking tower with {total_player_strength} troops")
                    old_owner = tower.owner  # Lưu owner cũ trước khi attack
                    was_captured = tower.receive_attack(total_player_strength, OwnerType.PLAYER)
                    if was_captured:
                        self._notify_tower_captured(tower, old_owner, OwnerType.PLAYER)
                    for i, _ in player_troops:
                        if i not in troops_to_remove:
                            troops_to_remove.append(i)
                
                if total_enemy_strength > 0:
                    print(f"Enemy attacking tower with {total_enemy_strength} troops")
                    old_owner = tower.owner  # Lưu owner cũ trước khi attack
                    was_captured = tower.receive_attack(total_enemy_strength, OwnerType.ENEMY)
                    if was_captured:
                        self._notify_tower_captured(tower, old_owner, OwnerType.ENEMY)
                    for i, _ in enemy_troops:
                        if i not in troops_to_remove:
                            troops_to_remove.append(i)
                
                if total_neutral_strength > 0:
                    print(f"Neutral attacking tower with {total_neutral_strength} troops")
                    old_owner = tower.owner  # Lưu owner cũ trước khi attack
                    was_captured = tower.receive_attack(total_neutral_strength, OwnerType.NEUTRAL)
                    if was_captured:
                        self._notify_tower_captured(tower, old_owner, OwnerType.NEUTRAL)
                    for i, _ in neutral_troops:
                        if i not in troops_to_remove:
                            troops_to_remove.append(i)
        
        # Remove arrived troops BEFORE checking combat
        for i in reversed(sorted(troops_to_remove)):
            if i < len(self._troops):
                del self._troops[i]
        
        # Sau khi xử lý tower arrivals, mới xử lý troop-to-troop combat
        self._handle_troop_combat()
    
    def _handle_troop_combat(self):
        """Xử lý combat giữa các troops với simplified collision detection - 1 vs 1 combat only"""
        troops_to_remove = []
        troops_in_combat = set()  # Track troops đã combat trong update này
        
        for i in range(len(self._troops)):
            if i in troops_to_remove or i in troops_in_combat:
                continue
                
            troop1 = self._troops[i]
            
            for j in range(i + 1, len(self._troops)):
                if j in troops_to_remove or j in troops_in_combat:
                    continue
                    
                troop2 = self._troops[j]
                
                # Enhanced collision detection cho troops khác owner
                if troop1.owner != troop2.owner:
                    # Kiểm tra distance trực tiếp
                    distance = ((troop1.x - troop2.x)**2 + (troop1.y - troop2.y)**2)**0.5
                    collision_threshold = troop1.radius + troop2.radius + 15  # Buffer zone
                    
                    if distance <= collision_threshold:
                        print(f"Combat detected: {troop1.owner} ({troop1.count}) at ({troop1.x:.1f},{troop1.y:.1f}) vs {troop2.owner} ({troop2.count}) at ({troop2.x:.1f},{troop2.y:.1f}) - distance: {distance:.1f}")
                        
                        # Thực hiện combat
                        winner1, winner2 = troop1.combat_with(troop2)
                        
                        # Mark cả 2 troops đã combat
                        troops_in_combat.add(i)
                        troops_in_combat.add(j)
                        
                        # Xử lý kết quả combat
                        if winner1 is None:
                            print(f"Troop1 ({troop1.owner}) defeated")
                            troops_to_remove.append(i)
                        if winner2 is None:
                            print(f"Troop2 ({troop2.owner}) defeated")
                            troops_to_remove.append(j)
                        
                        # Play combat sound
                        self.notify("combat_occurred", {
                            "winner": winner1.owner if winner1 else (winner2.owner if winner2 else "draw"),
                            "position": (troop1.x, troop1.y)
                        })
                        
                        # CRITICAL: Break sau combat để troop1 không combat với troops khác
                        break
        
        # Remove defeated troops
        for i in reversed(sorted(troops_to_remove)):
            if i < len(self._troops):
                print(f"Removing defeated troop at index {i}")
                del self._troops[i]
    
    def _find_target_tower(self, troop: Troop) -> Optional[Tower]:
        """Tìm tower mà troop đang chạm với improved detection để catch troops sớm hơn"""
        target_x, target_y = troop.target_position
        
        # Tìm tower gần target position nhất
        closest_tower = None
        min_distance_to_target = float('inf')
        
        for tower in self._towers:
            # Kiểm tra distance từ troop position đến tower
            distance_from_troop = ((tower.x - troop.x)**2 + (tower.y - troop.y)**2)**0.5
            distance_from_target = ((tower.x - target_x)**2 + (tower.y - target_y)**2)**0.5
            
            # Enhanced collision detection với larger buffer để catch troops sớm hơn
            tower_collision_radius = tower.radius + troop.radius + 20  # Increased buffer
            
            # PRIORITY 1: Troop đã trong vùng collision của tower
            if distance_from_troop <= tower_collision_radius:
                print(f"Direct collision: Troop at ({troop.x:.1f}, {troop.y:.1f}) hit tower at ({tower.x}, {tower.y}) - distance: {distance_from_troop:.1f}")
                return tower
            
            # Track closest tower to target for secondary check
            if distance_from_target < min_distance_to_target:
                min_distance_to_target = distance_from_target
                closest_tower = tower
        
        # PRIORITY 2: Fallback - return closest tower if target is very close to it
        if closest_tower and min_distance_to_target <= closest_tower.radius + 5:
            # Additional check: troop should be moving towards this tower
            troop_to_closest = ((closest_tower.x - troop.x)**2 + (closest_tower.y - troop.y)**2)**0.5
            if troop_to_closest <= closest_tower.radius + 30:  # Generous buffer
                print(f"Fallback collision: Troop at ({troop.x:.1f}, {troop.y:.1f}) caught by closest tower at ({closest_tower.x}, {closest_tower.y})")
                return closest_tower
            
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
        self._spawn_queue.clear()  # Clear spawn queue
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
        """Tạo towers ban đầu theo config của level với vị trí động"""
        import random
        
        # Calculate dynamic positions
        positions = self._calculate_tower_positions()
        
        # Tạo player towers
        player_positions = positions['player']
        for i in range(level_config['player_towers']):
            if i < len(player_positions):
                x, y = player_positions[i]
                tower = PlayerTower(x, y, level_config['initial_troops'])
                self._towers.append(tower)
        
        # Tạo enemy towers
        enemy_positions = positions['enemy']
        for i in range(level_config['enemy_towers']):
            if i < len(enemy_positions):
                x, y = enemy_positions[i]
                enemy_troops = level_config.get('enemy_initial_troops', level_config['initial_troops'])
                tower = EnemyTower(x, y, enemy_troops)
                self._towers.append(tower)
                
        # Tạo neutral towers
        neutral_positions = positions['neutral'].copy()
        random.shuffle(neutral_positions)  # Shuffle để có variation
        for i in range(level_config['neutral_towers']):
            if i < len(neutral_positions):
                x, y = neutral_positions[i]
                neutral_troops = random.randint(5, 15)  # Random troops for neutral towers
                tower = Tower(x, y, OwnerType.NEUTRAL, neutral_troops)
                self._towers.append(tower)
        
        enemy_troops = level_config.get('enemy_initial_troops', level_config['initial_troops'])
        player_troops = level_config['initial_troops']
        print(f"Created level: {level_config['player_towers']} player towers ({player_troops} troops each), "
              f"{level_config['enemy_towers']} enemy towers ({enemy_troops} troops each), "
              f"{level_config['neutral_towers']} neutral towers (dynamic positioning)")
    
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
