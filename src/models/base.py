"""
Base classes và interfaces cho game Tower War
Thể hiện tính Abstraction và Polymorphism trong OOP
"""
from abc import ABC, abstractmethod
import pygame
from typing import Tuple, Optional

class GameObject(ABC):
    """
    Abstract base class cho tất cả game objects
    Thể hiện tính Abstraction - ẩn implementation details
    """
    
    def __init__(self, x: float, y: float):
        self._x = x  # Encapsulation - protected attribute
        self._y = y
        self._active = True
    
    @property
    def x(self) -> float:
        """Getter cho x coordinate - Encapsulation"""
        return self._x
    
    @x.setter
    def x(self, value: float):
        """Setter cho x coordinate - Encapsulation"""
        self._x = value
    
    @property
    def y(self) -> float:
        """Getter cho y coordinate - Encapsulation"""
        return self._y
    
    @y.setter
    def y(self, value: float):
        """Setter cho y coordinate - Encapsulation"""
        self._y = value
    
    @property
    def position(self) -> Tuple[float, float]:
        """Trả về vị trí dưới dạng tuple"""
        return (self._x, self._y)
    
    @property
    def active(self) -> bool:
        """Kiểm tra object có đang active không"""
        return self._active
    
    def deactivate(self):
        """Deactivate object"""
        self._active = False
    
    @abstractmethod
    def update(self, dt: float):
        """
        Abstract method để update object
        Mỗi subclass phải implement method này
        """
        pass
    
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """
        Abstract method để vẽ object
        Mỗi subclass phải implement method này
        """
        pass

class Drawable(ABC):
    """
    Interface cho các object có thể vẽ được
    """
    
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Vẽ object lên screen"""
        pass

class Clickable(ABC):
    """
    Interface cho các object có thể click được
    """
    
    @abstractmethod
    def contains_point(self, x: float, y: float) -> bool:
        """Kiểm tra xem điểm (x, y) có nằm trong object không"""
        pass
    
    @abstractmethod
    def on_click(self, pos: Tuple[float, float]) -> Optional[object]:
        """Xử lý sự kiện click"""
        pass

class Movable(ABC):
    """
    Interface cho các object có thể di chuyển
    """
    
    @abstractmethod
    def move(self, dt: float):
        """Di chuyển object"""
        pass

class Observer(ABC):
    """
    Observer pattern interface
    """
    
    @abstractmethod
    def update_observer(self, event_type: str, data: dict):
        """Cập nhật khi có sự kiện"""
        pass

class Subject:
    """
    Subject class cho Observer pattern
    """
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: Observer):
        """Đăng ký observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Hủy đăng ký observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: dict = None):
        """Thông báo cho tất cả observers"""
        if data is None:
            data = {}
        for observer in self._observers:
            observer.update_observer(event_type, data)
