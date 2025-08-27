
# Design Patterns Implementation in Tower War Game


## 1. Creational Patterns

### Singleton Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `GameController`
- **Description**: Ensures there is only one instance of GameController throughout the game.

### Factory Pattern
- **File**: `src/controllers/game_controller.py`
- **Class**: `TowerFactory`
- **Description**: Creates different types of towers (Player, Enemy, Neutral).


## 2. Structural Patterns

### Facade Pattern (Indirect)
- **File**: `main.py`
- **Class**: `TowerWarGame` (or main function)
- **Description**: Initializes and connects MVC components, simplifies game startup.

### Composite Pattern
- **File**: `src/views/game_view.py`
- **Class**: `GameView`
- **Description**: Manages and draws multiple UI components, effects, and HUD.


## 3. Behavioral Patterns

### Observer Pattern
- **Files**: 
  - `src/models/base.py` (Observer, Subject)
  - `src/controllers/game_controller.py` 
  - `src/views/game_view.py`, `src/views/ui_view.py`
- **Description**: Model/Controller notify View when there are changes/events.

### Strategy Pattern
- **File**: `src/controllers/ai_controller.py`
- **Classes**: `AIStrategy`, `AggressiveStrategy`, `DefensiveStrategy`, `SmartStrategy`
- **Description**: AI changes behavior based on strategy and difficulty.

### State Pattern
- **File**: `src/utils/constants.py`, `src/controllers/game_controller.py`
- **Class**: `GameState`
- **Description**: Manages game state (PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE).

### Command Pattern (Indirect)
- **File**: `src/controllers/game_controller.py`
- **Method**: `handle_click`
- **Description**: Encapsulates click actions as command objects for processing.

### Template Method Pattern
- **File**: `src/views/ui_view.py`
- **Class**: `UIView` (abstract base)
- **Description**: Defines the skeleton for UI views, subclasses override the `draw` method.


## 4. Architectural Patterns

### Model-View-Controller (MVC)
- **Model**: `src/models/` - Tower, Troop, game data
- **View**: `src/views/` - UI rendering and presentation
- **Controller**: `src/controllers/` - Game logic and user input handling


## 5. OOP Principles

### Encapsulation
- **Files**: All model classes
- **Description**: Private/protected attributes, clear getter/setter methods.

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


## 6. Progression/Save System

### Progression Manager
- **File**: `src/utils/progression_manager.py`
- **Class**: `ProgressionManager`
- **Description**: Saves and loads game progress via JSON file.


## Summary
The project implements many popular Design Patterns (Singleton, Factory, Observer, Strategy, State, Composite, Template Method, MVC) and fully applies the 4 OOP principles.