
# Tower War Game - OOP Edition

**Development Team: Group 6**

**Members:**
- Do Duc Thinh - 24127123
- Chau Vu Trung - 24127256
- Vo Nguyen Khoa - 24127191
- Tran Gia Phuc - 24127221
---

Real-time strategy game developed in Python (pygame), OOP architecture, applying modern design patterns.


## 🏗️ Architecture & Project Structure

```
src/
├── models/          # Data models: Tower, Troop, base, interface
├── controllers/     # Game logic: GameController (Singleton), AIController (Strategy)
├── views/           # UI rendering: GameView, UIView, HUD, PauseMenu, GameOverScreen
├── utils/           # Utilities: constants, sound_manager, progression_manager, animation_manager
```

- **MVC Pattern**: Model (models), View (views), Controller (controllers)
- **Progression System**: Save progress with `progression_save.json`
- **Assets**: images/, sounds/, animations/


## 🔑 OOP & Design Patterns

- **Encapsulation**: Private/protected attributes, getter/setter
- **Inheritance**: 
   - `GameObject` <|= `Tower` <|= `PlayerTower`, `EnemyTower`
   - `GameObject` <|= `Troop` <|= `PlayerTroop`, `EnemyTroop`
   - `UIView` <|= `GameHUD`, `GameOverScreen`, `PauseMenu`
- **Polymorphism**: Override `draw()`, `update()`, `get_color()`
- **Abstraction**: Abstract base (`GameObject`, `UIView`, `AIStrategy`, `Observer`, `Subject`)
- **Singleton**: `GameController`
- **Factory**: `TowerFactory` creates tower types
- **Observer**: Model/Controller notify View on changes
- **Strategy**: AI changes behavior by difficulty
- **State**: `GameState` manages game state
- **Composite**: `GameView` manages multiple UI components
- **Template Method**: `UIView` defines UI skeleton


## 🎮 How to Play

- **Objective**: Capture all towers on the map to win.
- **Blue towers**: Yours, **Red**: AI, **Gray**: Neutral.
- **Troop growth**: Your/AI towers auto-increase troops, neutral towers do not.
- **Controls**: Click to select/deselect towers, send troops, preview paths.
- **Combat**: Troops arriving at an enemy tower reduce its count; if <=0, the tower changes owner.
- **Win**: All red towers become blue. **Lose**: The opposite.


## 🎯 Level & Progression System

- 3 levels with increasing difficulty, smarter AI at higher levels.
- Complete a level to unlock the next.
- Progress is saved automatically, continue with the **CONTINUE** button.
- Reset progress with **NEW GAME**.


## ⚙️ Installation & Run

### Run from Source

1. Install pygame:
   ```
   pip install pygame
   ```
2. Run the game:
   ```
   python main.py
   ```

### Build EXE (Windows)

1. Install cx_Freeze:
   ```
   pip install cx-Freeze
   ```
2. Build:
   ```
   python setup.py build
   ```
3. Run `TowerWar.exe` in the build folder.

> Make sure to copy all assets (images, sounds, animations) when building.


## 🕹️ Controls & UI Features

- **Left Mouse**: Select/deselect/send troops
- **ESC/SPACE**: Pause/Resume game
- **F11**: Fullscreen
- **Pause Menu**: Resume, Restart, Main Menu, Sound/Music toggle
- **Settings Menu**: Adjust sound, music, auto-save preferences
- **Level Select**: Choose level from menu
- **Dynamic Scaling**: UI auto-scales, supports all resolutions


## 💾 Save/Progression

- Progress is auto-saved to `progression_save.json`
- Continue from last completed level with **CONTINUE**
- Restart from the beginning with **NEW GAME**


## 🧠 Strategy Tips

- Defend strong towers, attack weak ones, expand via neutral towers, and take advantage of troop growth over time.

---

Enjoy the game and conquer every level of Tower War!
