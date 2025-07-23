"""
Troop model - thể hiện tính Inheritance, Encapsulation, Polymorphism
"""
import pygame
import math
from typing import Tuple
from ..models.base import GameObject, Movable
from ..utils.constants import Colors, GameSettings, OwnerType

class Troop(GameObject, Movable):
    """
    Lớp Troop kế thừa từ GameObject và implement Movable interface
    Đại diện cho các đơn vị quân di chuyển giữa các tower
    """
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float, 
                 owner: str, count: int):
        super().__init__(start_x, start_y)
        
        # Encapsulation - private attributes
        self.__target_x = target_x
        self.__target_y = target_y
        self.__owner = owner
        self.__count = count
        self.__speed = GameSettings.TROOP_SPEED
        self.__radius = GameSettings.TROOP_RADIUS
        
        # Tính toán vector di chuyển
        self.__dx, self.__dy = self.__calculate_movement_vector()
        
        # Validate input
        self.__validate_count(count)
        self.__validate_owner(owner)
    
    def __validate_count(self, count: int):
        """Private method để validate troops count"""
        if count <= 0:
            raise ValueError("Troop count must be positive")
    
    def __validate_owner(self, owner: str):
        """Private method để validate owner"""
        valid_owners = [OwnerType.PLAYER, OwnerType.ENEMY, OwnerType.NEUTRAL]
        if owner not in valid_owners:
            raise ValueError(f"Invalid owner: {owner}")
    
    def __calculate_movement_vector(self) -> Tuple[float, float]:
        """
        Private method để tính toán vector di chuyển
        Encapsulation - ẩn logic tính toán
        """
        distance = math.sqrt((self.__target_x - self.x)**2 + (self.__target_y - self.y)**2)
        if distance > 0:
            dx = (self.__target_x - self.x) / distance * self.__speed
            dy = (self.__target_y - self.y) / distance * self.__speed
            return dx, dy
        return 0.0, 0.0
    
    # Properties cho Encapsulation
    @property
    def target_position(self) -> Tuple[float, float]:
        """Getter cho target position"""
        return (self.__target_x, self.__target_y)
    
    @property
    def owner(self) -> str:
        """Getter cho owner"""
        return self.__owner
    
    @property
    def count(self) -> int:
        """Getter cho troop count"""
        return self.__count
    
    @property
    def radius(self) -> float:
        """Getter cho radius"""
        return self.__radius
    
    @property
    def speed(self) -> float:
        """Getter cho speed"""
        return self.__speed
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Polymorphism - method có thể được override
        Trả về màu sắc dựa trên owner
        """
        color_map = {
            OwnerType.PLAYER: Colors.BLUE,
            OwnerType.ENEMY: Colors.RED,
            OwnerType.NEUTRAL: Colors.GRAY
        }
        return color_map.get(self.__owner, Colors.GRAY)
    
    def update(self, dt: float):
        """
        Override abstract method từ GameObject
        Cập nhật vị trí troop
        """
        if not self.active:
            return
        
        # Di chuyển troop
        self.move(dt)
    
    def move(self, dt: float):
        """
        Implementation của Movable interface
        Di chuyển troop theo hướng đã tính toán
        """
        self.x += self.__dx * dt
        self.y += self.__dy * dt
    
    def has_reached_target(self) -> bool:
        """
        Kiểm tra xem troop đã đến đích chưa
        """
        distance_to_target = math.sqrt(
            (self.__target_x - self.x)**2 + (self.__target_y - self.y)**2
        )
        return distance_to_target <= self.__radius
    
    def draw(self, screen: pygame.Surface):
        """
        Override abstract method từ GameObject
        Vẽ troop lên screen
        """
        if not self.active:
            return
        
        # Vẽ troop
        color = self.get_color()
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.__radius)
        
        # Vẽ border
        pygame.draw.circle(screen, Colors.BLACK, (int(self.x), int(self.y)), 
                         self.__radius, 1)
        
        # Vẽ số quân
        self.__draw_count_text(screen)
    
    def __draw_count_text(self, screen: pygame.Surface):
        """Private method để vẽ số lượng quân - Encapsulation"""
        try:
            font = pygame.font.SysFont('Arial', GameSettings.FONT_SMALL, bold=True)
        except:
            font = pygame.font.Font(None, GameSettings.FONT_SMALL)
        
        text = font.render(str(self.__count), True, Colors.WHITE)
        text_rect = text.get_rect(center=(self.x, self.y - 15))
        
        # Vẽ background cho text để dễ đọc
        background_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(screen, Colors.BLACK, background_rect)
        pygame.draw.rect(screen, Colors.WHITE, background_rect, 1)
        
        screen.blit(text, text_rect)
    
    def distance_to_target(self) -> float:
        """Tính khoảng cách đến target"""
        return math.sqrt(
            (self.__target_x - self.x)**2 + (self.__target_y - self.y)**2
        )
    
    def distance_to_troop(self, other_troop: 'Troop') -> float:
        """Tính khoảng cách đến troop khác"""
        return math.sqrt(
            (other_troop.x - self.x)**2 + (other_troop.y - self.y)**2
        )
    
    def is_colliding_with(self, other_troop: 'Troop') -> bool:
        """
        Kiểm tra xem có collision với troop khác không
        Chỉ collision nếu khác owner
        """
        if self.__owner == other_troop.owner:
            return False
        
        collision_distance = self.__radius + other_troop.radius + 10  # Buffer zone
        return self.distance_to_troop(other_troop) <= collision_distance
    
    def combat_with(self, other_troop: 'Troop') -> Tuple['Troop', 'Troop']:
        """
        Combat logic: quân bé hơn bị mất, quân lớn hơn giảm = abs(lớn - bé)
        Returns: (winner_troop, None) hoặc (None, None) nếu hòa
        """
        if self.__owner == other_troop.owner:
            return self, other_troop  # Cùng phe, không đánh nhau
        
        my_count = self.__count
        other_count = other_troop.count
        
        if my_count > other_count:
            # Tôi thắng
            self.__count = my_count - other_count
            return self, None
        elif other_count > my_count:
            # Đối phương thắng
            other_troop._Troop__count = other_count - my_count  # Access private attribute
            return None, other_troop
        else:
            # Hòa nhau, cả hai bị tiêu diệt
            return None, None
    
    def __str__(self) -> str:
        """String representation của troop"""
        return f"Troop({self.__owner}, {self.__count} units) moving to ({self.__target_x}, {self.__target_y})"
    
    def __repr__(self) -> str:
        """Developer representation của troop"""
        return (f"Troop(x={self.x}, y={self.y}, target=({self.__target_x}, {self.__target_y}), "
                f"owner='{self.__owner}', count={self.__count})")

class PlayerTroop(Troop):
    """
    Subclass của Troop cho player troops
    Thể hiện tính Inheritance và Polymorphism
    """
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float, count: int):
        super().__init__(start_x, start_y, target_x, target_y, OwnerType.PLAYER, count)
        self.__morale_boost = 1.1  # Player troops move slightly faster
    
    def move(self, dt: float):
        """
        Override move method - Polymorphism
        Player troops move with morale boost
        """
        boosted_dt = dt * self.__morale_boost
        super().move(boosted_dt)
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Override get_color method - Polymorphism
        Player troops có highlight đặc biệt
        """
        base_color = super().get_color()
        # Thêm một chút highlight
        return tuple(min(255, c + 20) for c in base_color)

class EnemyTroop(Troop):
    """
    Subclass của Troop cho enemy troops
    Thể hiện tính Inheritance và Polymorphism
    """
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float, count: int):
        super().__init__(start_x, start_y, target_x, target_y, OwnerType.ENEMY, count)
        self.__aggression_factor = 1.05  # Enemy troops slightly more aggressive
    
    def move(self, dt: float):
        """
        Override move method - Polymorphism
        Enemy troops move with aggression factor
        """
        aggressive_dt = dt * self.__aggression_factor
        super().move(aggressive_dt)
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Override get_color method - Polymorphism
        Enemy troops có màu đỏ đậm hơn
        """
        return (255, 30, 30)  # Đỏ đậm hơn
