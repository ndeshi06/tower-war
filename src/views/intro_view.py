import pygame
import random

def show_intro(screen, max_duration=5000):
    """Hiển thị intro với loading bar + hiệu ứng fade-out chuyển cảnh"""
    clock = pygame.time.Clock()
    
    # Get initial screen dimensions
    width, height = screen.get_size()
    fullscreen = False
    
    # Import constants for reference resolution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

    # Font setup
    pygame.font.init()
    
    def get_scaled_fonts(scale_factor):
        """Get properly scaled fonts"""
        title_size = int(48 * scale_factor)
        percent_size = int(28 * scale_factor) 
        sub_size = int(24 * scale_factor)
        return (
            pygame.font.SysFont("Arial", title_size, bold=True),
            pygame.font.SysFont("Arial", percent_size),
            pygame.font.SysFont("Arial", sub_size, italic=True)
        )
    
    # Calculate initial scale factor
    scale_factor = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)
    title_font, percent_font, sub_font = get_scaled_fonts(scale_factor)

    from src.utils.sound_manager import SoundManager
    sound_manager = SoundManager()
    sound_manager.play_intro_music()
    
    # Colors
    background_color = (30, 30, 60)
    bar_bg_color = (50, 50, 80)
    bar_fill_color = (100, 200, 250)

    # Loading variables
    progress_percent = 0
    start_time = pygame.time.get_ticks()

    def toggle_fullscreen():
        """Toggle fullscreen mode"""
        nonlocal screen, fullscreen, width, height, scale_factor, title_font, percent_font, sub_font
        
        fullscreen = not fullscreen
        
        # Reset display to avoid issues
        pygame.display.quit()
        pygame.display.init()
        
        if fullscreen:
            # Native fullscreen resolution
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Windowed mode with original resolution
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Tower War")
        
        # Update dimensions and scaling
        width, height = screen.get_size()
        scale_factor = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)
        title_font, percent_font, sub_font = get_scaled_fonts(scale_factor)
    
    def draw_intro_content():
        """Draw intro content with proper scaling"""
        # Calculate layout based on current screen size and scaling
        if fullscreen:
            # For fullscreen, create a game surface and scale it
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Draw on game surface with scale factor 1.0
            game_surface.fill(background_color)
            
            # Get fonts for original resolution
            orig_title_font, orig_percent_font, orig_sub_font = get_scaled_fonts(1.0)
            
            # Group text
            group_text = orig_sub_font.render("A GAME MADE BY GROUP 6", True, (200, 200, 200))
            group_rect = group_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            
            # Progress bar on game surface
            bar_width = SCREEN_WIDTH // 2
            bar_height = 25
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = SCREEN_HEIGHT // 2
            
            # Loading text
            loading_text = orig_title_font.render(f"Loading... {progress_percent}%", True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            
            # Draw everything on game surface
            game_surface.blit(loading_text, loading_rect)
            game_surface.blit(group_text, group_rect)
            pygame.draw.rect(game_surface, bar_bg_color, (bar_x, bar_y, bar_width, bar_height), border_radius=12)
            fill_width = int(bar_width * progress_percent / 100)
            pygame.draw.rect(game_surface, bar_fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=12)
            
            # Scale and center on actual screen
            scale = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)
            scaled_width = int(SCREEN_WIDTH * scale)
            scaled_height = int(SCREEN_HEIGHT * scale)
            offset_x = (width - scaled_width) // 2
            offset_y = (height - scaled_height) // 2
            
            # Clear screen with black bars
            screen.fill((0, 0, 0))
            
            # Scale and blit game surface
            scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))
            screen.blit(scaled_surface, (offset_x, offset_y))
        else:
            # Windowed mode - direct drawing with scaling
            screen.fill(background_color)
            
            # Group text
            group_text = sub_font.render("A GAME MADE BY GROUP 6", True, (200, 200, 200))
            group_rect = group_text.get_rect(center=(width // 2, height // 2 + int(80 * scale_factor)))
            
            # Progress bar
            bar_width = int((SCREEN_WIDTH // 2) * scale_factor)
            bar_height = int(25 * scale_factor)
            bar_x = (width - bar_width) // 2
            bar_y = height // 2
            
            # Loading text
            loading_text = title_font.render(f"Loading... {progress_percent}%", True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(width // 2, height // 2 - int(80 * scale_factor)))
            
            # Draw everything
            screen.blit(loading_text, loading_rect)
            screen.blit(group_text, group_rect)
            pygame.draw.rect(screen, bar_bg_color, (bar_x, bar_y, bar_width, bar_height), border_radius=max(1, int(12 * scale_factor)))
            fill_width = int(bar_width * progress_percent / 100)
            pygame.draw.rect(screen, bar_fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=max(1, int(12 * scale_factor)))

    # Main loop
    running = True
    while running:
        dt = clock.tick(60)
        elapsed = pygame.time.get_ticks() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Handle F11 for fullscreen toggle
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()

        # Tăng % ngẫu nhiên (giả lập loading thực tế)
        if progress_percent < 100:
            increment = random.randint(1, 4)
            progress_percent += increment
            progress_percent = min(progress_percent, 100)
            pygame.time.delay(random.randint(50, 120))

        # Draw intro content
        draw_intro_content()
        pygame.display.flip()

        # Khi đủ 100%, chuyển qua hiệu ứng fade
        if progress_percent >= 100 or elapsed >= max_duration:
            fade_out(screen, clock)
            running = False
    
    return screen  # Return the current screen state for main.py

def fade_out(screen, clock, speed=10):
    """Hiệu ứng fade-out mượt"""
    fade_surface = pygame.Surface(screen.get_size()).convert_alpha()
    for alpha in range(0, 256, speed):
        fade_surface.fill((0, 0, 0, alpha))  # alpha từ 0 -> 255
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
