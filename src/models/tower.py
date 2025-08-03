"""
Tower model - thể hiện tính Inheritance, Encapsulation, Polymorphism
"""
import pygame
import math
import random
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
        
        # Load image manager
        from ..utils.image_manager import ImageManager
        self.image_manager = ImageManager()
        # self._flying_rocks = []  # Đã bỏ hiệu ứng đá bay
        # self.rock_image = self.image_manager.get_image('flying_rock')

        #Load sound manager
        from ..utils.sound_manager import SoundManager
        self.sound_manager = SoundManager()
        self.sound_manager.preload()

        self._scale = 1.0  # scale mặc định
        self._scale_velocity = 0.0  # tốc độ scale để giật

        self._rotation = 0.0           # Góc xoay hiện tại
        self._rotation_velocity = 0.0  # Tốc độ xoay để rung    

        
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
    
    # Images manager

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
    
    def set_troop_count(self, new_count):
        if new_count > self.troop_count:
            self.bump_animation()
        self._prev_troop_count = self.troop_count
        self.troops = new_count

    def trigger_bump(self):
        """Gây hiệu ứng giật - dùng khi tăng quân"""
        self._scale = 1.2
        self._scale_velocity = -0.02
        self._rotation = 5
        self._rotation_velocity = -0.5
    

    # Sound manager

    def on_troop_gain(self, amount=1, from_team=None, auto=False):
        self.troop_count += amount
        now = pygame.time.get_ticks()
        if auto:
            if now - self.last_self_gain_sound > 500:  # 500ms cooldown
                self.SoundManager().play("self_gain", volume=0.3)
                self.last_self_gain_sound = now
    
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

        # Hiệu ứng giật
        if value != old_troops:
            self.trigger_bump()
        
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
                self.sound_manager.play("self_gain", volume=0.5)
            self.__last_growth_time = current_time
        
        # Scale hiệu ứng mượt
        if self._scale_velocity != 0:
            self._scale += self._scale_velocity
            if self._scale > 1.2:
                self._scale = 1.2
                self._scale_velocity *= -1
            elif self._scale < 1.0:
                self._scale = 1.0
                self._scale_velocity = 0

        # Xoay hiệu ứng mượt
        if self._rotation_velocity != 0:
            self._rotation += self._rotation_velocity
            if abs(self._rotation) > 5:  # Giật tối đa 5 độ
                self._rotation_velocity *= -1
            elif abs(self._rotation) < 0.5:
                self._rotation = 0
                self._rotation_velocity = 0
    
    def draw(self, screen: pygame.Surface):
        """
        Override abstract method từ GameObject
        Vẽ tower lên screen với image nếu có
        """

        if not self.active:
            return
            
        # Lấy image dựa trên owner và số quân
        if self.__troops < 5:
            image_name = f"tower_{self.__owner}_3"
        elif self.__troops < 10:
            image_name = f"tower_{self.__owner}_2"
        else:
            image_name = f"tower_{self.__owner}"
        tower_image = self.image_manager.get_image(image_name)
        
        if tower_image:
            scaled_size = (
                int(tower_image.get_width() * self._scale),
                int(tower_image.get_height() * self._scale)
            )
            # Chỉ gọi scale một lần
            scaled_image = pygame.transform.smoothscale(tower_image, scaled_size)
            # Xoay
            rotated_image = pygame.transform.rotate(scaled_image, self._rotation)
            # Căn giữa lại đúng tọa độ gốc
            image_rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            # Vẽ lên màn hình
            screen.blit(rotated_image, image_rect)
        else:
            # Fallback: vẽ bằng circle như cũ
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
            # Scale font size based on current scale
            font_size = max(12, int(GameSettings.FONT_MEDIUM * self._scale))
            font = pygame.font.SysFont('Arial', font_size, bold=True)
        except:
            # Fallback nếu không có Arial
            font_size = max(12, int(GameSettings.FONT_MEDIUM * self._scale))
            font = pygame.font.Font(None, font_size)
        
        text = font.render(str(self.__troops), True, Colors.WHITE)
        text_rect = text.get_rect(midbottom=(self.x, self.y - self.radius - int(4 * self._scale)))
        
        # Vẽ shadow cho text để dễ đọc hơn
        shadow = font.render(str(self.__troops), True, Colors.BLACK)
        shadow_rect = shadow.get_rect(midbottom=(self.x + 1, self.y - self.radius - int(3 * self._scale)))

        screen.blit(shadow, shadow_rect)
        screen.blit(text, text_rect)
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        Implementation của Clickable interface
        Kiểm tra xem điểm có nằm trong tower không
        Sử dụng hitbox lớn hơn để dễ click hơn
        """
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        # Hitbox lớn hơn 50% so với visual radius để dễ click
        click_radius = self.__radius * 1.5
        return distance <= click_radius
    
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
        result = self.__troops > 0 and self.__owner != OwnerType.NEUTRAL
        print(f"Tower can_send_troops: troops={self.__troops}, owner={self.__owner}, result={result}")
        return result
    
    def send_troops(self, target: 'Tower') -> int:
        """
        Gửi quân đến tower khác
        Trả về số quân được gửi
        """
        print(f"Tower send_troops called: can_send={self.can_send_troops()}")
        
        if not self.can_send_troops():
            print(f"Tower send_troops: Cannot send troops")
            return 0
        
        # Đảm bảo gửi ít nhất 1 troop, nhưng không gửi hết
        troops_to_send = max(1, self.__troops // 2)
        if troops_to_send >= self.__troops:
            troops_to_send = self.__troops - 1  # Giữ lại ít nhất 1 troop
        
        if troops_to_send <= 0:
            print(f"Tower send_troops: No troops to send (calculated {troops_to_send})")
            return 0
            
        print(f"Tower send_troops: Sending {troops_to_send} troops, remaining {self.__troops - troops_to_send}")
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
            self.sound_manager.play("troop_add")
            self.troops = self.__troops + attacking_troops
            return False
        else:
            # Khác phe, giảm quân
            self.sound_manager.play("troop_remove")

            # Bỏ tạo đá bay khi bị tấn công

            if attacking_troops >= self.__troops:
                # Tower bị chiếm
                remaining_troops = attacking_troops - self.__troops
                old_owner = self.__owner
                self.owner = attacker_owner  # Sử dụng setter để trigger notification
                self.troops = remaining_troops
                if remaining_troops > 0: # hiệu ứng giật
                    self.trigger_bump()
                print(f"Tower captured! {old_owner} -> {attacker_owner} với {remaining_troops} quân")
                return True
            else:
                # Tower không bị chiếm, chỉ giảm quân
                self.troops = self.__troops - attacking_troops
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
