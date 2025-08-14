# Design Patterns Implementation trong Tower War Game

## 1. Creational Patterns

### Singleton Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `GameController`
- **Mô tả**: Đảm bảo chỉ có một instance của GameController trong toàn bộ game.

### Factory Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `TowerFactory`
- **Mô tả**: Tạo các loại towers khác nhau (Player, Enemy, Neutral).

## 2. Structural Patterns

### Facade Pattern (Gián tiếp)
- **File**: `main.py`
- **Class**: `TowerWarGame` (hoặc hàm main)
- **Mô tả**: Khởi tạo và kết nối các thành phần MVC, đơn giản hóa khởi động game.

### Composite Pattern
- **File**: `src/views/game_view.py`
- **Class**: `GameView`
- **Mô tả**: Quản lý và vẽ nhiều UI component, hiệu ứng, HUD.

## 3. Behavioral Patterns

### Observer Pattern
- **Files**: 
  - `src/models/base.py` (Observer, Subject)
  - `src/controllers/game_controller.py` 
  - `src/views/game_view.py`, `src/views/ui_view.py`
- **Mô tả**: Model/Controller notify View khi có sự kiện thay đổi.

### Strategy Pattern
- **File**: `src/controllers/ai_controller.py`
- **Classes**: `AIStrategy`, `AggressiveStrategy`, `DefensiveStrategy`, `SmartStrategy`
- **Mô tả**: AI thay đổi hành vi dựa trên chiến lược và độ khó.

### State Pattern
- **File**: `src/utils/constants.py`, `src/controllers/game_controller.py`
- **Class**: `GameState`
- **Mô tả**: Quản lý trạng thái game (PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE).

### Command Pattern (Gián tiếp)
- **File**: `src/controllers/game_controller.py`
- **Method**: `handle_click`
- **Mô tả**: Đóng gói thao tác click thành các hành động xử lý.

### Template Method Pattern
- **File**: `src/views/ui_view.py`
- **Class**: `UIView` (abstract base)
- **Mô tả**: Định nghĩa khung cho các UI view, các class con override method `draw`.

## 4. Architectural Patterns

### Model-View-Controller (MVC)
- **Model**: `src/models/` - Tower, Troop, game data
- **View**: `src/views/` - UI rendering và presentation
- **Controller**: `src/controllers/` - Game logic và user input handling

## 5. OOP Principles

### Encapsulation
- **Files**: Tất cả model classes
- **Mô tả**: Thuộc tính private/protected, getter/setter rõ ràng.

### Inheritance
- **Hierarchy**: 
  - `GameObject` <|= `Tower` <|= `PlayerTower`, `EnemyTower`
  - `GameObject` <|= `Troop` <|= `PlayerTroop`, `EnemyTroop`
  - `UIView` <|= `GameHUD`, `GameOverScreen`, `PauseMenu`

### Polymorphism
- **Method Overriding**: `draw()`, `update()`, `get_color()`

### Abstraction
- **Abstract Classes**: `GameObject`, `UIView`, `AIStrategy`, `Observer`, `Subject`
- **Interfaces**: `Clickable`, `Movable`, `Drawable`

## 6. Progression/Lưu game

### Progression Manager
- **File**: `src/utils/progression_manager.py`
- **Class**: `ProgressionManager`
- **Mô tả**: Lưu và tải tiến trình game qua file JSON.

## Tổng kết
Project implement nhiều Design Patterns phổ biến (Singleton, Factory, Observer, Strategy, State, Composite, Template Method, MVC) và đầy đủ 4 nguyên lý OOP.