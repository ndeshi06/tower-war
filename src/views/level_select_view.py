"""
Level Selection View - UI cho chọn level
"""
import pygame
from ..utils.constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, GameSettings

class LevelSelectView:
    """UI cho việc chọn level"""
    
    def __init__(self, screen=None, level_manager=None):
        # Screen reference for scaling
        self.screen = screen
        # Level manager reference
        self.level_manager = level_manager
        
        # Initialize fonts với Unicode support
        pygame.font.init()
        try:
            # Sử dụng system font có hỗ trợ tiếng Việt
            self.font_title = pygame.font.SysFont('arial', 48, bold=True)
            self.font_button = pygame.font.SysFont('arial', 32)
            self.font_desc = pygame.font.SysFont('arial', 24)
        except:
            # Fallback với font mặc định
            self.font_title = pygame.font.Font(None, 48)
            self.font_button = pygame.font.Font(None, 32)
            self.font_desc = pygame.font.Font(None, 24)
        
        # Level buttons
        self.level_buttons = []
        self.back_button = None
        self.setup_buttons()
        
        # Animation
        self.hover_button = None
        self.animation_time = 0
        
    def setup_buttons(self):
        """Setup level buttons"""
        button_width = 320  # Tăng từ 250 lên 320 để chữ không bị tràn
        button_height = 100  # Tăng từ 90 lên 100 cho nhiều space hơn
        spacing = 40
        
        # Tính toán để căn giữa toàn bộ nhóm buttons
        total_height = 3 * button_height + 2 * spacing
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        levels = [
            {"name": "Level 1", "desc": "Easy - 3 vs 2", "difficulty": "Easy"},
            {"name": "Level 2", "desc": "Medium - 2 vs 3", "difficulty": "Medium"},
            {"name": "Level 3", "desc": "Hard - 2 vs 4", "difficulty": "Hard"}
        ]
        
        for i, level in enumerate(levels):
            # Căn giữa chính xác theo chiều ngang - will be recalculated in draw()
            x = (1024 - button_width) // 2  # Use default size, will be updated dynamically
            y = start_y + i * (button_height + spacing)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.level_buttons.append({
                "rect": button_rect,
                "level": i + 1,
                "name": level["name"],
                "desc": level["desc"],
                "difficulty": level["difficulty"]
            })
        
        # Back button
        back_x = 50
        back_y = SCREEN_HEIGHT - 100
        self.back_button = pygame.Rect(back_x, back_y, 120, 50)
    
    def handle_event(self, event):
        """Xử lý events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check level buttons
                for button in self.level_buttons:
                    if button["rect"].collidepoint(event.pos):
                        level = button['level']
                        # Kiểm tra level có mở khóa không
                        if self.level_manager and not self.level_manager.is_level_unlocked(level):
                            print(f"Level {level} is locked!")
                            return None  # Không cho phép chọn level bị khóa
                        return f"level_{level}"
                
                # Check back button
                if self.back_button.collidepoint(event.pos):
                    return "back_to_menu"
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hover_button = None
            for button in self.level_buttons:
                if button["rect"].collidepoint(event.pos):
                    level = button['level']
                    # Chỉ hover được khi level đã mở khóa
                    if not self.level_manager or self.level_manager.is_level_unlocked(level):
                        self.hover_button = button
                    break
            
            if self.back_button.collidepoint(event.pos):
                self.hover_button = "back"
        
        return None
    
    def _recalculate_buttons(self, screen_width, screen_height):
        """Recalculate button positions for current screen size"""
        button_width = 320  # Tăng từ 250 lên 320 để chữ không bị tràn
        button_height = 100  # Tăng từ 90 lên 100 cho nhiều space hơn
        spacing = 40
        
        # Tính toán để căn giữa toàn bộ nhóm buttons
        total_height = 3 * button_height + 2 * spacing
        start_y = (screen_height - total_height) // 2
        
        for i, button in enumerate(self.level_buttons):
            # Căn giữa chính xác theo chiều ngang
            button_x = (screen_width - button_width) // 2
            button_y = start_y + i * (button_height + spacing)
            button["rect"] = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Back button
        back_x = 50
        back_y = screen_height - 100
        self.back_button = pygame.Rect(back_x, back_y, 120, 50)
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
    
    def draw(self, screen):
        """Vẽ level selection screen"""
        # Get current screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Background
        screen.fill(Colors.LIGHT_BLUE)
        
        # Title - căn giữa và cách từ top
        title_text = self.font_title.render("Select Level", True, Colors.DARK_BLUE)
        title_rect = title_text.get_rect(center=(screen_width // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Recalculate button positions for current screen size
        self._recalculate_buttons(screen_width, screen_height)
        
        # Level buttons
        for button in self.level_buttons:
            self._draw_level_button(screen, button)
        
        # Progress info (hiển thị trạng thái mở khóa)
        if self.level_manager:
            self._draw_unlock_info(screen, screen_width, screen_height)
        
        # Back button
        self._draw_back_button(screen)
    
    def _draw_level_button(self, screen, button):
        """Vẽ level button"""
        rect = button["rect"]
        level = button["level"]
        is_unlocked = not self.level_manager or self.level_manager.is_level_unlocked(level)
        is_hovered = self.hover_button == button and is_unlocked
        
        # Button background - khác màu cho locked levels
        if not is_unlocked:
            color = Colors.LIGHT_GRAY
            border_color = Colors.GRAY
            border_width = 2
        else:
            color = Colors.WHITE if not is_hovered else Colors.LIGHT_GREEN
            border_color = Colors.DARK_BLUE if not is_hovered else Colors.GREEN
            border_width = 3 if not is_hovered else 5
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, border_color, rect, border_width)
        
        # Level name với màu khác cho locked
        text_color = Colors.GRAY if not is_unlocked else Colors.DARK_BLUE
        name_text = self.font_button.render(button["name"], True, text_color)
        name_rect = name_text.get_rect(center=(rect.centerx, rect.centery - 20))  # Tăng spacing
        screen.blit(name_text, name_rect)
        
        # Description
        desc_color = Colors.LIGHT_GRAY if not is_unlocked else Colors.DARK_BLUE
        desc_text = self.font_desc.render(button["desc"], True, desc_color)
        desc_rect = desc_text.get_rect(center=(rect.centerx, rect.centery + 5))  # Điều chỉnh position
        screen.blit(desc_text, desc_rect)
        
        # Difficulty hoặc lock status
        if not is_unlocked:
            # Hiển thị yêu cầu mở khóa thay vì emoji có thể gây lỗi font
            lock_text = self.font_desc.render("LOCKED", True, Colors.RED)
            lock_rect = lock_text.get_rect(center=(rect.centerx, rect.centery + 35))  # Tăng spacing
            screen.blit(lock_text, lock_rect)
        else:
            diff_text = self.font_desc.render(f"Difficulty: {button['difficulty']}", True, Colors.RED)
            diff_rect = diff_text.get_rect(center=(rect.centerx, rect.centery + 35))  # Tăng spacing
            screen.blit(diff_text, diff_rect)
    
    def _draw_back_button(self, screen):
        """Vẽ back button"""
        is_hovered = self.hover_button == "back"
        
        color = Colors.LIGHT_GRAY if not is_hovered else Colors.WHITE
        border_color = Colors.BLACK if not is_hovered else Colors.DARK_BLUE
        border_width = 2 if not is_hovered else 3
        
        pygame.draw.rect(screen, color, self.back_button)
        pygame.draw.rect(screen, border_color, self.back_button, border_width)
        
        # Text
        text = self.font_button.render("← Menu", True, Colors.BLACK)
        text_rect = text.get_rect(center=self.back_button.center)
        screen.blit(text, text_rect)
    
    def _draw_unlock_info(self, screen, screen_width, screen_height):
        """Vẽ thông tin về trạng thái mở khóa"""
        if not self.level_manager:
            return
            
        # Vị trí info ở giữa màn hình, dưới các buttons
        info_y = screen_height - 180
        
        # Completed levels
        completed_count = len(self.level_manager.levels_completed)
        total_levels = self.level_manager.max_level
        
        progress_text = f"Progress: {completed_count}/{total_levels} levels completed"
        progress_surface = self.font_desc.render(progress_text, True, Colors.DARK_BLUE)
        progress_rect = progress_surface.get_rect(center=(screen_width // 2, info_y))
        screen.blit(progress_surface, progress_rect)
        
        # Unlock requirement cho level tiếp theo
        for level in range(2, total_levels + 1):
            if not self.level_manager.is_level_unlocked(level):
                requirement_text = f"Complete Level {level - 1} to unlock Level {level}"
                requirement_surface = self.font_desc.render(requirement_text, True, Colors.RED)
                requirement_rect = requirement_surface.get_rect(center=(screen_width // 2, info_y + 25))
                screen.blit(requirement_surface, requirement_rect)
                break  # Chỉ hiển thị requirement cho level tiếp theo gần nhất
