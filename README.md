# Tower War Game - OOP Edition

**Nhóm phát triển: Group 6**

**Thành viên:**
- Đỗ Đức Thịnh - 24127123
- Châu Vũ Trung - 24127256
- Võ Nguyên Khoa - 24127191
- Trần Gia Phúc - 24127221
---

Game chiến thuật thời gian thực phát triển bằng Python (pygame), kiến trúc OOP, áp dụng nhiều design pattern hiện đại.

## 🏗️ Kiến trúc & Cấu trúc Project

```
src/
├── models/          # Data models: Tower, Troop, base, interface
├── controllers/     # Game logic: GameController (Singleton), AIController (Strategy)
├── views/           # UI rendering: GameView, UIView, HUD, PauseMenu, GameOverScreen
├── utils/           # Tiện ích: constants, sound_manager, progression_manager, animation_manager
```

- **MVC Pattern**: Model (models), View (views), Controller (controllers)
- **Progression System**: Lưu tiến trình với `progression_save.json`
- **Assets**: images/, sounds/, animations/

## 🔑 OOP & Design Patterns

- **Encapsulation**: Thuộc tính private/protected, getter/setter
- **Inheritance**: 
  - `GameObject` <|= `Tower` <|= `PlayerTower`, `EnemyTower`
  - `GameObject` <|= `Troop` <|= `PlayerTroop`, `EnemyTroop`
  - `UIView` <|= `GameHUD`, `GameOverScreen`, `PauseMenu`
- **Polymorphism**: Override `draw()`, `update()`, `get_color()`
- **Abstraction**: Abstract base (`GameObject`, `UIView`, `AIStrategy`, `Observer`, `Subject`)
- **Singleton**: `GameController`
- **Factory**: `TowerFactory` tạo các loại tower
- **Observer**: Model/Controller notify View khi thay đổi
- **Strategy**: AI thay đổi hành vi theo độ khó
- **State**: `GameState` quản lý trạng thái game
- **Composite**: `GameView` quản lý nhiều UI component
- **Template Method**: `UIView` định nghĩa khung cho UI

## 🎮 Cách chơi

- **Mục tiêu**: Chiếm toàn bộ tower trên bản đồ để thắng.
- **Tower xanh**: của bạn, **đỏ**: AI, **xám**: trung lập.
- **Tăng quân**: Tower của bạn/AI tự tăng quân, trung lập không tăng.
- **Điều khiển**: Click chọn/bỏ chọn tower, gửi quân, preview đường đi.
- **Chiến đấu**: Quân đến tower khác phe sẽ trừ quân, <=0 thì đổi phe.
- **Thắng**: Khi tất cả tower đỏ thành xanh. **Thua**: Ngược lại.

## 🎯 Hệ thống Level & Progression

- 3 level độ khó tăng dần, AI thông minh hơn ở level cao.
- Hoàn thành level để mở khóa level tiếp theo.
- Tiến trình lưu tự động, có thể tiếp tục bằng nút **CONTINUE**.
- Reset tiến trình bằng **NEW GAME**.

## ⚙️ Cài đặt & Chạy

### Chạy từ Source

1. Cài pygame:
   ```
   pip install pygame
   ```
2. Chạy game:
   ```
   python main.py
   ```

### Build EXE (Windows)

1. Cài cx_Freeze:
   ```
   pip install cx-Freeze
   ```
2. Build:
   ```
   python setup.py build
   ```
3. Chạy file `TowerWar.exe` trong thư mục build.

> Đảm bảo copy đủ assets (images, sounds, animations) khi build.

## 🕹️ Điều khiển & Tính năng UI

- **Chuột trái**: Chọn/bỏ chọn/gửi quân
- **ESC/SPACE**: Pause/Resume game
- **F11**: Fullscreen
- **Pause Menu**: Resume, Restart, Main Menu, Sound/Music toggle
- **Settings Menu**: Điều chỉnh âm thanh, nhạc nền, tự động lưu preferences
- **Level Select**: Chọn level từ menu
- **Dynamic Scaling**: UI tự động scale, hỗ trợ mọi độ phân giải

## 💾 Save/Progression

- Tự động lưu tiến trình vào `progression_save.json`
- Tiếp tục game từ level đã qua với **CONTINUE**
- Chơi lại từ đầu với **NEW GAME**

## 🧠 Chiến thuật gợi ý

- Phòng thủ tower mạnh, tấn công tower yếu, mở rộng bằng tower trung lập, tận dụng tăng quân theo thời gian.

---

Chúc bạn chơi vui vẻ và chinh phục mọi level của Tower War!
