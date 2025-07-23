"""
Tower model - thể hiện tính Inheritance, Encapsulation, Polymorphism
"""
import pygame
import math
from typing import Optional, Tuple
from ..models.base import GameObject, Clickable, Subject
from ..utils.constants import Colors, GameSettings, OwnerType

class Tower(GameObject, Clickable, Subject):
    """
    Lớp Tower kế thừa từ GameObject, implement Clickable interface
    và Subject cho Observer pattern
    """
    
    def __init__(self, x: float, y: float, owner: str = OwnerType.NEUTRAL, troops: int = 20):
        # Gọi constructor của parent classes
        GameObject.__init__(self, x, y)
        Subject.__init__(self)
        
        # Encapsulation - private và protected attributes
        self.__owner = owner
        self.__troops = troops
        self.__max_troops = GameSettings.TOWER_MAX_TROOPS
        self.__radius = GameSettings.TOWER_RADIUS
        self.__growth_rate = GameSettings.TOWER_GROWTH_RATE
        self.__last_growth_time = pygame.time.get_ticks()
        self._selected = False
        
        # Validate input
        self.__validate_owner(owner)
        self.__validate_troops(troops)
    
    def __validate_owner(self, owner: str):
        """Private method để validate owner - Encapsulation"""
        valid_owners = [OwnerType.PLAYER, OwnerType.ENEMY, OwnerType.NEUTRAL]
        if owner not in valid_owners:
            raise ValueError(f"Invalid owner: {owner}. Must be one of {valid_owners}")
    
    def __validate_troops(self, troops: int):
        """Private method để validate troops count - Encapsulation"""
        if troops < 0:
            raise ValueError("Troops count cannot be negative")
        if troops > self.__max_troops:
            # Allow temporary exceeding during processing, but cap it
            pass
    
    # Properties cho Encapsulation
    @property
    def owner(self) -> str:
        """Getter cho owner"""
        return self.__owner
    
    @owner.setter
    def owner(self, value: str):
        """Setter cho owner với validation"""
        old_owner = self.__owner
        self.__validate_owner(value)
        self.__owner = value
        # Notify observers về sự thay đổi owner
        self.notify("owner_changed", {
            "tower": self,
            "old_owner": old_owner,
            "new_owner": value
        })
    
    @property
    def troops(self) -> int:
        """Getter cho troops"""
        return self.__troops
    
    @troops.setter
    def troops(self, value: int):
        """Setter cho troops với validation"""
        self.__validate_troops(value)
        old_troops = self.__troops
        self.__troops = min(value, self.__max_troops)
        
        # Notify observers về sự thay đổi troops
        self.notify("troops_changed", {
            "tower": self,
            "old_troops": old_troops,
            "new_troops": self.__troops
        })
    
    @property
    def max_troops(self) -> int:
        """Getter cho max troops"""
        return self.__max_troops
    
    @property
    def radius(self) -> float:
        """Getter cho radius"""
        return self.__radius
    
    @property
    def selected(self) -> bool:
        """Getter cho selected state"""
        return self._selected
    
    @selected.setter
    def selected(self, value: bool):
        """Setter cho selected state"""
        self._selected = value
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Polymorphism - method có thể được override bởi subclass
        Trả về màu sắc tương ứng với owner
        """
        color_map = {
            OwnerType.PLAYER: Colors.BLUE,
            OwnerType.ENEMY: Colors.RED,
            OwnerType.NEUTRAL: Colors.GRAY
        }
        return color_map.get(self.__owner, Colors.GRAY)
    
    def can_grow(self) -> bool:
        """Kiểm tra xem tower có thể tăng quân không"""
        return self.__owner != OwnerType.NEUTRAL and self.__troops < self.__max_troops
    
    def update(self, dt: float):
        """
        Override abstract method từ GameObject
        Cập nhật trạng thái tower
        """
        if not self.active:
            return
            
        # Tăng quân mỗi giây (trừ tower neutral)
        current_time = pygame.time.get_ticks()
        if current_time - self.__last_growth_time >= 1000:  # 1 giây
            if self.can_grow():
                self.troops = self.__troops + self.__growth_rate
            self.__last_growth_time = current_time
    
    def draw(self, screen: pygame.Surface):
        """
        Override abstract method từ GameObject
        Vẽ tower lên screen
        """
        if not self.active:
            return
            
        # Vẽ selection highlight
        if self._selected:
            pygame.draw.circle(screen, Colors.WHITE, 
                             (int(self.x), int(self.y)), 
                             self.__radius + 5, 3)
        
        # Vẽ tower
        color = self.get_color()
        pygame.draw.circle(screen, color, 
                         (int(self.x), int(self.y)), 
                         self.__radius)
        pygame.draw.circle(screen, Colors.BLACK, 
                         (int(self.x), int(self.y)), 
                         self.__radius, 2)
        
        # Vẽ số quân với font đẹp hơn
        self.__draw_troops_text(screen)
    
    def __draw_troops_text(self, screen: pygame.Surface):
        """Private method để vẽ text số quân - Encapsulation"""
        try:
            # Sử dụng system font thay vì None để tránh lỗi
            font = pygame.font.SysFont('Arial', GameSettings.FONT_MEDIUM, bold=True)
        except:
            # Fallback nếu không có Arial
            font = pygame.font.Font(None, GameSettings.FONT_MEDIUM)
        
        text = font.render(str(self.__troops), True, Colors.WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        
        # Vẽ shadow cho text để dễ đọc hơn
        shadow = font.render(str(self.__troops), True, Colors.BLACK)
        shadow_rect = shadow.get_rect(center=(self.x + 1, self.y + 1))
        screen.blit(shadow, shadow_rect)
        screen.blit(text, text_rect)
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        Implementation của Clickable interface
        Kiểm tra xem điểm có nằm trong tower không
        """
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.__radius
    
    def on_click(self, pos: Tuple[float, float]) -> Optional['Tower']:
        """
        Implementation của Clickable interface
        Xử lý sự kiện click vào tower
        """
        x, y = pos
        if self.contains_point(x, y):
            self.notify("tower_clicked", {"tower": self, "position": pos})
            return self
        return None
    
    def can_send_troops(self) -> bool:
        """Kiểm tra xem có thể gửi quân không"""
        return self.__troops > 1 and self.__owner != OwnerType.NEUTRAL
    
    def send_troops(self, target: 'Tower') -> int:
        """
        Gửi quân đến tower khác
        Trả về số quân được gửi
        """
        if not self.can_send_troops():
            return 0
        
        troops_to_send = self.__troops // 2
        self.troops = self.__troops - troops_to_send
        
        # Notify observers
        self.notify("troops_sent", {
            "source": self,
            "target": target,
            "troops_count": troops_to_send
        })
        
        return troops_to_send
    
    def receive_attack(self, attacking_troops: int, attacker_owner: str) -> bool:
        """
        Nhận tấn công từ quân địch
        Trả về True nếu tower bị chiếm
        """
        if self.__owner == attacker_owner:
            # Cùng phe, tăng quân
            self.troops = self.__troops + attacking_troops
            return False
        else:
            # Khác phe, giảm quân
            new_troops_count = self.__troops - attacking_troops
            if new_troops_count <= 0:
                # Tower bị chiếm
                remaining_troops = abs(new_troops_count)
                old_owner = self.__owner
                self.owner = attacker_owner  # Sử dụng setter để trigger notification
                self.troops = remaining_troops
                print(f"Tower captured! {old_owner} -> {attacker_owner} với {remaining_troops} quân")
                return True
            else:
                # Tower không bị chiếm, chỉ giảm quân
                self.troops = new_troops_count
                return False
    
    def distance_to(self, other: 'Tower') -> float:
        """Tính khoảng cách đến tower khác"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __str__(self) -> str:
        """String representation của tower"""
        return f"Tower({self.owner}, {self.__troops} troops) at ({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        """Developer representation của tower"""
        return (f"Tower(x={self.x}, y={self.y}, owner='{self.__owner}', "
                f"troops={self.__troops}, max_troops={self.__max_troops})")

class PlayerTower(Tower):
    """
    Subclass của Tower cho player towers
    Thể hiện tính Inheritance và Polymorphism
    """
    
    def __init__(self, x: float, y: float, troops: int = 30):
        super().__init__(x, y, OwnerType.PLAYER, troops)
        self.__upgrade_level = 1
    
    @property
    def upgrade_level(self) -> int:
        """Getter cho upgrade level"""
        return self.__upgrade_level
    
    def upgrade(self):
        """Upgrade tower để tăng growth rate"""
        if self.__upgrade_level < 3:
            self.__upgrade_level += 1
            self._Tower__growth_rate += 1  # Name mangling để access private attribute
            self.notify("tower_upgraded", {"tower": self, "level": self.__upgrade_level})
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Override method của parent class - Polymorphism
        Player tower có màu khác dựa trên upgrade level, nhưng phải check owner hiện tại
        """
        # Nếu owner đã thay đổi, sử dụng màu theo owner mới
        if self.owner != OwnerType.PLAYER:
            color_map = {
                OwnerType.ENEMY: Colors.RED,
                OwnerType.NEUTRAL: Colors.GRAY
            }
            return color_map.get(self.owner, Colors.GRAY)
        
        # Nếu vẫn là player tower, màu theo upgrade level
        if self.__upgrade_level == 1:
            return Colors.BLUE
        elif self.__upgrade_level == 2:
            return Colors.LIGHT_BLUE
        else:
            return Colors.DARK_BLUE

class EnemyTower(Tower):
    """
    Subclass của Tower cho enemy towers
    Thể hiện tính Inheritance và Polymorphism
    """
    
    def __init__(self, x: float, y: float, troops: int = 30):
        super().__init__(x, y, OwnerType.ENEMY, troops)
        self.__aggression_level = 1
    
    @property
    def aggression_level(self) -> int:
        """Getter cho aggression level"""
        return self.__aggression_level
    
    def increase_aggression(self):
        """Tăng độ hung hăng của AI"""
        if self.__aggression_level < 3:
            self.__aggression_level += 1
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Override method của parent class - Polymorphism
        Enemy tower có màu đỏ đậm hơn khi aggression cao, nhưng phải check owner hiện tại
        """
        # Nếu owner đã thay đổi, sử dụng màu theo owner mới
        if self.owner != OwnerType.ENEMY:
            color_map = {
                OwnerType.PLAYER: Colors.BLUE,
                OwnerType.NEUTRAL: Colors.GRAY
            }
            return color_map.get(self.owner, Colors.GRAY)
        
        # Nếu vẫn là enemy tower, màu theo aggression level
        base_red = 255
        green_blue = max(50 - (self.__aggression_level * 20), 0)
        return (base_red, green_blue, green_blue)
