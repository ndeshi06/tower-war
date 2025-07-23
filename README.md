# Tower War Game - OOP Edition

Một game chiến thuật thời gian thực được phát triển bằng pygame Python với kiến trúc OOP hoàn chỉnh.

## 🏗️ Kiến trúc OOP

### Cấu trúc Project
```
src/
├── models/          # Data models (MVC Pattern)
│   ├── base.py      # Abstract classes và interfaces
│   ├── tower.py     # Tower classes với inheritance
│   └── troop.py     # Troop classes với polymorphism
├── controllers/     # Game logic controllers
│   ├── ai_controller.py    # AI với Strategy Pattern
│   └── game_controller.py  # Main game logic với Singleton
├── views/          # UI và rendering (MVC Pattern)
│   ├── game_view.py    # Main game renderer
│   └── ui_view.py      # UI components
└── utils/
    └── constants.py    # Game constants và enums
```

### Các tính chất OOP được áp dụng:

#### 1. **Encapsulation (Đóng gói)**
- Private attributes với `__` prefix
- Properties với getter/setter
- Validation trong constructors
- Protected data access

#### 2. **Inheritance (Kế thừa)**
- `Tower` → `PlayerTower`, `EnemyTower`
- `Troop` → `PlayerTroop`, `EnemyTroop`
- `GameObject` → `Tower`, `Troop`
- Abstract base classes

#### 3. **Polymorphism (Đa hình)**
- Method overriding (`get_color()`, `move()`)
- Interface implementation
- Duck typing với Abstract methods

#### 4. **Abstraction (Trừu tượng)**
- Abstract base classes (`GameObject`, `UIView`)
- Interfaces (`Clickable`, `Movable`, `Drawable`)
- Strategy Pattern cho AI behavior

### Design Patterns được sử dụng:

1. **MVC Pattern**: Model-View-Controller separation
2. **Observer Pattern**: Event-driven architecture
3. **Strategy Pattern**: AI behavior strategies
4. **Singleton Pattern**: GameController
5. **Factory Pattern**: Tower creation
6. **Template Method Pattern**: Game loop structure
7. **Facade Pattern**: Main game class

## 🎮 Cách chơi

### Mục tiêu
Chiếm tất cả các tower trên bản đồ để giành chiến thắng.

### Luật chơi

1. **Các loại Tower:**
   - **Tower xanh**: Thuộc về người chơi
   - **Tower đỏ**: Thuộc về kẻ thù (AI)
   - **Tower xám**: Tower trung lập (chưa ai chiếm)

2. **Thông số Tower:**
   - Mỗi tower có một số lượng quân nhất định
   - Tower của player và enemy sẽ tự động tăng 1 quân mỗi giây
   - Tower trung lập không tự động tăng quân
   - Giới hạn tối đa: 50 quân/tower

3. **Điều khiển:**
   - Click vào tower xanh của bạn để chọn
   - Click vào tower khác để gửi quân tấn công
   - Mỗi lần gửi sẽ chuyển một nửa số quân hiện có

4. **Chiến đấu:**
   - Khi quân đến tower cùng phe: Số quân tower tăng lên
   - Khi quân đến tower khác phe: Số quân tower giảm xuống
   - Nếu số quân tower <= 0: Tower đổi màu theo phe tấn công

5. **Điều kiện thắng thua:**
   - Thắng: Khi tất cả towers đỏ đều thuộc về bạn (màu xanh)
   - Thua: Khi tất cả towers xanh đều thuộc về AI (màu đỏ)

## Cài đặt và chạy

1. Cài đặt pygame:
```bash
pip install pygame
```

2. Chạy game:
```bash
python main.py
```

## 🎮 Điều khiển nâng cao

### Game Controls
- **Click chuột trái**: Chọn tower và gửi quân
- **ESC**: Pause/Resume game

### AI Difficulty
- **Easy mode**
- **Medium mode**
- **Hard mode**

## Chiến thuật

1. **Phòng thủ**: Giữ những tower quan trọng có nhiều quân
2. **Tấn công**: Tập trung quân để chiếm tower yếu
3. **Mở rộng**: Chiếm tower trung lập để tăng sức mạnh
4. **Thời gian**: Tận dụng việc tower tự động tăng quân theo thời gian

Chúc bạn chơi vui vẻ!
