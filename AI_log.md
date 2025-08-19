# AI_log.md - Nhật ký phát triển Tower War Game
# Models nhóm sử dụng : Claude Sonnet 4, GPT 4.1
## Tổng quan dự án
- **Tên game**: Tower War
- **Ngôn ngữ**: Python với pygame
- **Kiến trúc**: MVC (Model-View-Controller) với Design Patterns
- **Mục tiêu**: Game chiến thuật thời gian thực với AI thông minh

## Các vấn đề đã khắc phục

### 1. Lỗi ImageManager 
- **Vấn đề**: `'ImageManager' object has no attribute 'get_image'`
- **Nguyên nhân**: Thiếu method `get_image()` trong ImageManager
- **Giải pháp**: Thêm method mapping từ tên image đến file với fallback rendering

### 2. Lỗi pause menu và ESC key
- **Vấn đề**: 
  - ESC thoát game thay vì pause
  - Pause menu chưa hoạt động đúng
- **Giải pháp**:
  - Sửa ESC để pause thay vì quit
  - Cải thiện pause menu với Observer pattern

### 3. Thiếu UI pause dialog
- **Vấn đề**: Game pause không có hộp thoại lựa chọn
- **Giải pháp**: Thêm dialog pause với buttons "Tiếp tục" và "Ra menu"

### 4. Lỗi troops âm
- **Vấn đề**: `ValueError: Troops count cannot be negative`
- **Nguyên nhân**: Logic trong `receive_attack()` có thể gán số quân âm
- **Giải pháp**: Sửa logic để kiểm tra `attacking_troops >= self.__troops` trước khi tính toán

### 5. Hệ thống Level progression
- **Vấn đề**: Không có progression
- **Giải pháp**: 
  - Tạo 3 levels với độ khó tăng dần
  - Level 1 (Easy)
  - Level 2 (Medium)
  - Level 3 (Hard)
  - Thêm LevelManager với State pattern
  - Level selection UI với các nút chọn level

### 6. Game Result UI System
- **Vấn đề**: Cần UI để xử lý win/lose và chuyển level
- **Giải pháp**:
  - Tạo GameResultView với win/lose screens
  - Win screen: Nút "Next Level" hoặc "Main Menu"
  - Lose screen: Nút "Play Again" hoặc "Main Menu" 
  - Support cho "All Levels Complete" khi thắng hết

### 7. Font và Unicode Issues
- **Vấn đề**: 
  - Lỗi font với tiếng Việt 
  - Unicode characters gây crash
  - UI text bị lỗi hiển thị
- **Giải pháp**:
  - Chuyển tất cả text sang tiếng Anh
  - Sử dụng system fonts với Unicode support
  - Thêm fallback font handling
  - Loại bỏ emoji/special characters

## Kết quả đạt được

- Đã khắc phục các lỗi chạy chương trình chính
- Hoàn thiện kiến trúc hướng đối tượng với mô hình MVC
- Hệ thống hiển thị ổn định với phương án dự phòng  
- Điều khiển game hoạt động mượt mà
- Trí tuệ nhân tạo thông minh với 3 mức độ khó khác nhau
- Hệ thống tạm dừng/tiếp tục hoàn chỉnh với giao diện
- Cơ chế chiếm đóng tháp đầy đủ
- Mã nguồn được ghi chú chi tiết
- Đóng gói dữ liệu đúng với thuộc tính riêng tư/bảo vệ
- Cây thừa kế rõ ràng (Tower → PlayerTower/EnemyTower)
- Đa hình trong chiến lược AI và hành vi Tower
- Quản lý hình ảnh với name mapping và fallback rendering
- Kiểm tra số quân để tránh giá trị âm
- Hệ thống giải thích AI cho 3 chiến lược

## Các Prompt quan trọng và Output Analysis


### 1. Prompt lỗi ImageManager  
**User Input**: "Game báo lỗi: Không tìm thấy hàm get_image trong ImageManager"

**AI Output**:
Tôi thấy lỗi là trong `ImageManager` không có method `get_image()`. Hãy sửa lại file `src/utils/image_manager.py`:

```python
def get_image(self, name: str) -> Optional[pygame.Surface]:
    """
    Lấy image theo tên
    Returns: pygame.Surface hoặc None nếu không tìm thấy
    """
    # Mapping từ tên logic sang filename
    name_to_file = {
        'tower_player': 'tower_player.png',
        'tower_enemy': 'tower_enemy.png', 
        'tower_neutral': 'tower_neutral.png',
        'background': 'background.png'
    }
    
    filename = name_to_file.get(name)
    if filename:
        return self.load_image(filename)
    return None
```

**Đánh giá**: Rất hữu ích, đã áp dụng đúng đoạn code AI gợi ý vào file `src/utils/image_manager.py`. Việc bổ sung hàm `get_image` giúp quản lý hình ảnh logic hơn, khắc phục hoàn toàn lỗi không tìm thấy method và giúp code dễ bảo trì.

### 2. Prompt pause menu issues
**User Input**: "Tôi muốn khi ấn ESC thì game thoát ra menu thay vì tạm dừng, và không hiện hộp thoại win/lose"

**AI Output**:
Tôi sẽ sửa lỗi ESC và thêm hộp thoại win/lose. Vấn đề chính là:

1. ESC đang quit thay vì pause
2. Thiếu win/lose detection
3. Pause menu chưa hoạt động đúng

Sửa lại trong `main.py`:

```python
elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_ESCAPE:
        if self.game_state == "playing":
            self.pause_game()  # Thay vì self.running = False
        elif self.game_state == "paused":
            self.resume_game()
```

Và thêm method pause_game():

```python
def pause_game(self):
    """Tạm dừng game"""
    self.game_state = "paused"
    self.controller.notify("game_paused", {})
```

**Đánh giá**: Hữu ích, đã chỉnh lại logic phím ESC và thêm method `pause_game` vào `main.py` như AI hướng dẫn. Game đã tạm dừng đúng ý, code rõ ràng hơn, tuy nhiên phát sinh một số lỗi phụ cần xử lý tiếp.

### 3. Prompt UI pause improvement
**User Input**: "Tôi muốn khi game pause thì hiện hộp thoại với nút Tiếp tục và Ra menu"

**AI Output**:
Tôi sẽ cải thiện pause menu để hiển thị dialog với lựa chọn. Sửa trong `src/views/ui_view.py`:

```python
def draw_pause_menu(self, screen: pygame.Surface):
    """Vẽ pause menu với dialog và buttons"""
    # Vẽ overlay mờ
    overlay = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(Colors.BLACK)
    screen.blit(overlay, (0, 0))
    
    # Dialog box
    dialog_width, dialog_height = 400, 250
    dialog_x = (GameSettings.SCREEN_WIDTH - dialog_width) // 2
    dialog_y = (GameSettings.SCREEN_HEIGHT - dialog_height) // 2
    
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, Colors.WHITE, dialog_rect)
    pygame.draw.rect(screen, Colors.BLACK, dialog_rect, 3)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render("GAME PAUSED", True, Colors.BLACK)
    title_rect = title.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 60))
    screen.blit(title, title_rect)
    
    # Buttons
    button_font = pygame.font.Font(None, 36)
    
    # Continue button
    continue_text = button_font.render("Tiếp tục (SPACE)", True, Colors.WHITE)
    continue_rect = pygame.Rect(dialog_x + 50, dialog_y + 120, 300, 40)
    pygame.draw.rect(screen, Colors.GREEN, continue_rect)
    pygame.draw.rect(screen, Colors.BLACK, continue_rect, 2)
    text_rect = continue_text.get_rect(center=continue_rect.center)
    screen.blit(continue_text, text_rect)
    
    # Menu button  
    menu_text = button_font.render("Ra Menu (M)", True, Colors.WHITE)
    menu_rect = pygame.Rect(dialog_x + 50, dialog_y + 170, 300, 40)
    pygame.draw.rect(screen, Colors.RED, menu_rect)
    pygame.draw.rect(screen, Colors.BLACK, menu_rect, 2)
    text_rect = menu_text.get_rect(center=menu_rect.center)
    screen.blit(menu_text, text_rect)
```

**Đánh giá**: Rất hữu ích, đã bổ sung hàm `draw_pause_menu` vào `src/views/ui_view.py` theo đúng hướng dẫn. Giao diện pause menu trực quan, các nút hoạt động đúng, nâng cao trải nghiệm người dùng.

### 4. Prompt negative troops bug
**User Input**: "Game bị crash khi troops tấn công và chiếm được tower"

**AI Output**:
Tôi thấy lỗi xảy ra khi tower nhận tấn công và số quân trở thành âm. Vấn đề là trong method `receive_attack`, code đang gán số quân âm vào property `troops`, nhưng setter của `troops` có validation không cho phép số âm. Hãy sửa lỗi này:

```python
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
        if attacking_troops >= self.__troops:
            # Tower bị chiếm
            remaining_troops = attacking_troops - self.__troops
            old_owner = self.__owner
            self.owner = attacker_owner  # Sử dụng setter để trigger notification
            self.troops = remaining_troops
            print(f"Tower captured! {old_owner} -> {attacker_owner} với {remaining_troops} quân")
            return True
        else:
            # Tower không bị chiếm, chỉ giảm quân
            self.troops = self.__troops - attacking_troops
            return False
```

Vấn đề đã được khắc phục! Lỗi xảy ra vì logic cũ có thể tạo ra số quân âm, nhưng logic mới đảm bảo không có số quân âm nào được gán vào property `troops`.

**Đánh giá**: Đã fix được lỗi quan trọng khiến game crash.

### 5. Prompt AI explanation
**User Input**: "Hãy giải thích cách chơi của AI địch"

**AI Output**:
Dựa trên code AI controller, tôi sẽ giải thích cách hoạt động của AI địch trong game:

## Hệ thống AI có 3 mức độ khó:

### 1. **Easy (DefensiveStrategy)**:
- **Chiến thuật bảo thủ**: AI chỉ tấn công khi có ít nhất 5 quân trong tower
- **Ưu tiên neutral towers**: AI sẽ chiếm neutral towers trước thay vì tấn công player
- **Tốc độ chậm**: Hành động mỗi 4 giây
- **Logic**: Tìm neutral tower gần nhất, nếu không có thì tấn công player tower yếu nhất

### 2. **Medium (SmartStrategy)**:
- **Thích ứng tình hình**: AI thay đổi chiến thuật dựa trên tương quan sức mạnh
- **Aggressive khi mạnh**: Nếu AI có >120% quân so với player → tấn công liên tục
- **Defensive khi yếu**: Nếu AI có <80% quân so với player → tập trung bảo vệ
- **Mixed strategy**: Khi cân bằng sức mạnh → kết hợp cả hai
- **Tốc độ trung bình**: Hành động mỗi 3 giây

### 3. **Hard (AggressiveStrategy)**:
- **Tấn công liên tục**: AI tấn công ngay khi có >1 quân
- **Chọn target gần nhất**: Ưu tiên tấn công tower gần để giảm thời gian di chuyển
- **Tốc độ nhanh**: Hành động mỗi 2 giây
- **Logic đơn giản**: Chọn tower mạnh nhất → tấn công target gần nhất

## Cơ chế hoạt động:

1. **Action Interval**: AI kiểm tra có nên hành động không dựa trên timer
2. **Strategy Pattern**: Mỗi difficulty sử dụng strategy khác nhau
3. **Decision Making**: AI đánh giá towers có sẵn và chọn source + target optimal
4. **Statistics Tracking**: AI theo dõi success rate và performance metrics

## Ví dụ decision process của SmartStrategy:
```python
enemy_strength = sum(t.troops for t in enemy_towers)  
player_strength = sum(t.troops for t in player_towers)

if enemy_strength > player_strength * 1.2:
    # AI mạnh hơn → aggressive: tấn công player tower yếu nhất
    return aggressive_action()
elif enemy_strength < player_strength * 0.8:  
    # AI yếu hơn → defensive: chiếm neutral towers
    return defensive_action()
else:
    # Cân bằng → mixed: random giữa aggressive và defensive
    return mixed_action()
```

AI sẽ thông minh hơn ở mức Hard và có thể thích ứng tình huống ở mức Medium, tạo ra trải nghiệm chơi đa dạng cho người chơi.

**Đánh giá**: Hữu ích, giải thích dễ hiểu, rất cần để hiểu logic của AI Controller.

### 6. Prompt level system implementation
**User Input**: "Hãy thêm hệ thống level với khoảng 2-3 level tăng dần mức độ khó, hiện tại chỉ có 1 level."

**AI Output**:
Tôi sẽ thêm hệ thống level với 3 mức độ khó tăng dần. Đây là cách triển khai:

1. **Tạo LevelConfig trong constants.py**:
```python
@dataclass
class LevelConfig:
    level_id: int
    name: str
    player_towers: int
    enemy_towers: int
    neutral_towers: int
    ai_difficulty: str
    description: str
```

2. **Cập nhật LevelManager**:
```python
def advance_to_next_level(self) -> bool:
    """Chuyển sang level tiếp theo"""
    if self.current_level < len(LEVEL_CONFIGS):
        self.current_level += 1
        return True
    return False  # Đã hoàn thành tất cả levels
```

3. **Logic chuyển level trong main.py**:
- Win level → advance_to_next_level()
- Lose level → restart current level
- Auto-progression với Observer pattern

**Đánh giá**: Đã tạo được hệ thống 3 levels với độ khó tăng dần và logic chuyển level tự động.

### 7. Prompt UI improvement
**User Input**: "Tôi muốn hiện giao diện trung gian để chọn level"

**AI Output**:
Tôi sẽ tạo UI system hoàn chỉnh với level selection và result screens:

1. **LevelSelectView**: UI chọn level với thông tin difficulty
2. **GameResultView**: Win/lose screens với navigation options
3. **App state management**: "menu" → "level_select" → "game" → "result"

Cấu trúc UI flow:
```
Main Menu → Level Select → Game → Result Screen
     ↑         ↑          ↓         ↓
     └─────────┴──────────┴─────────┘
```

**Đánh giá**: Tạo được UI flow hoàn chỉnh, user experience mượt mà với nhiều navigation options.

### 8. Prompt font issues
**User Input**: "lỗi font tiếng việt, lỗi hộp thoại: khi win-lose game thì hộp thoại bị nhấp nháy"

**AI Output**:
Tôi thấy có 2 vấn đề chính:

1. **Font Unicode issues**: pygame không handle tiếng Việt tốt
2. **UI flickering**: Render logic không ổn định

Giải pháp:
```python
# Sử dụng system font với Unicode support
self.font = pygame.font.SysFont('arial', 24)

# Fix UI state để tránh flickering
if self.app_state == "result" and not self.result_processed:
    self.result_processed = True
    # Handle result logic once
```

**Đánh giá**: Đã giải quyết được hầu hết các lỗi ở prompt nhưng chưa ổn định.

### 9. Prompt convert to English
**User Input**: "Hãy chuyển hết text trong ui sang tiếng anh"

**AI Output**:
Tôi sẽ chuyển toàn bộ UI text sang tiếng Anh để tránh Unicode issues...

**Đánh giá**: Giải pháp đơn giản và hiệu quả, hoàn toàn loại bỏ vấn đề với Unicode.

### 10. Prompt thêm hiệu ứng chiến thắng/thua cuộc
**User Input**: "Khi win hoặc lose, có thể thêm hiệu ứng animation hoặc âm thanh đặc biệt không?"

**AI Output**:
Có thể thêm hiệu ứng bằng cách:
- Thêm animation vào `GameResultView` khi win/lose.
- Phát âm thanh đặc biệt trong `sound_manager.py` khi kết thúc trận đấu.
- Sử dụng hiệu ứng chuyển cảnh trong `transition.py` để tăng trải nghiệm.


### 11. Prompt lưu và tải lại tiến trình game
**User Input**: "Muốn lưu lại tiến trình game và cho phép người chơi bấm Continue để chơi tiếp từ level trước"

**AI Output**:
- Sử dụng `progression_manager.py` để lưu trạng thái level vào file `progression_save.json`.
- Khi vào game, kiểm tra file lưu và load level tương ứng.
- Thêm nút "Continue" ở menu chính để tiếp tục từ level đã lưu.

**Đánh giá**: Hữu ích, đã triển khai lưu tiến trình game bằng `progression_manager.py` và thêm nút "Continue" vào menu chính như AI đề xuất. Người chơi có thể tiếp tục từ level đã qua, kiểm tra thực tế hoạt động ổn định, code dễ mở rộng cho các tính năng save/load khác.


**Ngày hoàn thành**: 23/07/2025