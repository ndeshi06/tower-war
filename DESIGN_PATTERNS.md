# Design Patterns Implementation trong Tower War Game

## 1. Creational Patterns

### Singleton Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `GameController`
- **Mô tả**: Đảm bảo chỉ có một instance của GameController trong toàn bộ game
```python
class GameController(Subject, Observer):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

### Factory Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `TowerFactory`
- **Mô tả**: Tạo các loại towers khác nhau (Player, Enemy, Neutral)
```python
class TowerFactory:
    @staticmethod
    def create_player_tower(x: float, y: float) -> PlayerTower:
        return PlayerTower(x, y, troops=30)
    
    @staticmethod
    def create_enemy_tower(x: float, y: float) -> EnemyTower:
        return EnemyTower(x, y, troops=30)
```

## 2. Structural Patterns

### Facade Pattern
- **File**: `main.py`
- **Class**: `TowerWarGame`
- **Mô tả**: Cung cấp interface đơn giản cho complex subsystem (MVC components)
```python
class TowerWarGame:
    def __init__(self):
        # Game components (MVC Pattern)
        self.controller = GameController()  # Model + Controller
        self.view = GameView(self.screen)   # View
```

### Adapter Pattern (Implicit)
- **File**: `src/views/game_view.py`
- **Mô tả**: GameView adapts game model data cho UI rendering

## 3. Behavioral Patterns

### Observer Pattern
- **Files**: 
  - `src/models/base.py` (Observer, Subject interfaces)
  - `src/controllers/game_controller.py` 
  - `src/views/game_view.py`
  - `src/views/ui_view.py`
- **Mô tả**: Towers notify GameController về events, GameController notify Views
```python
class Observer(ABC):
    @abstractmethod
    def update_observer(self, event_type: str, data: dict):
        pass

class Subject(ABC):
    def notify(self, event_type: str, data: dict):
        for observer in self._observers:
            observer.update_observer(event_type, data)
```

### Strategy Pattern
- **File**: `src/controllers/ai_controller.py`
- **Classes**: `AIStrategy`, `AggressiveStrategy`, `DefensiveStrategy`, `SmartStrategy`
- **Mô tả**: AI có thể thay đổi behavior dựa trên difficulty
```python
class AIStrategy(ABC):
    @abstractmethod
    def decide_action(self, enemy_towers: List[Tower], all_towers: List[Tower]) -> Optional[dict]:
        pass

class AggressiveStrategy(AIStrategy):
    def decide_action(self, enemy_towers, all_towers):
        # Aggressive AI logic
        pass
```

### Template Method Pattern
- **Files**: 
  - `src/views/ui_view.py` (UIView abstract class)
  - `main.py` (game loop structure)
- **Mô tả**: Định nghĩa skeleton của algorithms
```python
class UIView(ABC):
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass
    
    def get_font(self, size: int, bold: bool = False):
        # Template implementation
        pass
```

### State Pattern
- **File**: `src/controllers/game_controller.py`
- **Mô tả**: Game state management (PLAYING, PAUSED, GAME_OVER)
```python
def update(self, dt: float):
    if self._game_state != GameState.PLAYING:
        return
    # Game logic chỉ chạy khi PLAYING
```

### Command Pattern (Implicit)
- **File**: `src/controllers/game_controller.py`
- **Mô tả**: Handle click events như commands
```python
def handle_click(self, position: Tuple[float, float]):
    # Encapsulate click actions as commands
```

## 4. Architectural Patterns

### Model-View-Controller (MVC)
- **Model**: `src/models/` - Tower, Troop, game data
- **View**: `src/views/` - UI rendering và presentation
- **Controller**: `src/controllers/` - Game logic và user input handling

## 5. OOP Principles

### Encapsulation
- **Files**: Tất cả model classes
- **Mô tả**: Private attributes với getters/setters
```python
class Tower(GameObject):
    def __init__(self, x: float, y: float, owner: str = OwnerType.NEUTRAL, troops: int = 20):
        self.__owner = owner      # Private
        self.__troops = troops    # Private
    
    @property
    def owner(self) -> str:       # Public getter
        return self.__owner
```

### Inheritance
- **Hierarchy**: 
  - `GameObject` -> `Tower` -> `PlayerTower`, `EnemyTower`
  - `GameObject` -> `Troop` -> `PlayerTroop`, `EnemyTroop`
  - `UIView` -> `GameHUD`, `GameOverScreen`, `PauseMenu`

### Polymorphism
- **Method Overriding**: `get_color()`, `draw()`, `update()` methods
```python
class PlayerTower(Tower):
    def get_color(self) -> Tuple[int, int, int]:
        # Override parent method - different behavior
        if self.owner != OwnerType.PLAYER:
            return color_map.get(self.owner, Colors.GRAY)
        return Colors.BLUE  # Player-specific color
```

### Abstraction
- **Abstract Classes**: `GameObject`, `UIView`, `AIStrategy`, `Observer`, `Subject`
- **Interfaces**: `Clickable`, `Movable`, `Drawable`

## 6. Additional Patterns

### Repository Pattern (Implicit)
- **File**: `src/controllers/game_controller.py`
- **Mô tả**: GameController manages collections of towers và troops

### Composite Pattern (Implicit)
- **File**: `src/views/game_view.py`
- **Mô tả**: GameView composites multiple UI components

## Tổng kết
Project này implement **15+ Design Patterns** và demonstrate tất cả **4 OOP principles**:
1. **Encapsulation** - Private attributes, public interfaces
2. **Inheritance** - Class hierarchies
3. **Polymorphism** - Method overriding, interface implementation  
4. **Abstraction** - Abstract classes và interfaces