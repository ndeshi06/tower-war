import pygame
import random

def show_intro(screen, max_duration=5000):
    """Hiển thị intro với loading bar + hiệu ứng fade-out chuyển cảnh"""
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    # Font setup
    pygame.font.init()
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    percent_font = pygame.font.SysFont("Arial", 28)
    sub_font = pygame.font.SysFont("Arial", 24, italic=True)

    group_text = sub_font.render("A GAME MADE BY GROUP 6", True, (200, 200, 200))
    group_rect = group_text.get_rect(center=(width // 2, height // 2 + 80))

    # Colors
    background_color = (30, 30, 60)
    bar_bg_color = (50, 50, 80)
    bar_fill_color = (100, 200, 250)

    # Progress bar
    bar_width = width // 2
    bar_height = 25
    bar_x = (width - bar_width) // 2
    bar_y = height // 2

    # Loading variables
    progress_percent = 0
    start_time = pygame.time.get_ticks()

    # Main loop
    running = True
    while running:
        dt = clock.tick(60)
        elapsed = pygame.time.get_ticks() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Tăng % ngẫu nhiên (giả lập loading thực tế)
        if progress_percent < 100:
            increment = random.randint(1, 4)
            progress_percent += increment
            progress_percent = min(progress_percent, 100)
            pygame.time.delay(random.randint(50, 120))

        # Vẽ nền
        screen.fill(background_color)

        # Vẽ text
        loading_text = title_font.render(f"Loading... {progress_percent}%", True, (255, 255, 255))
        loading_rect = loading_text.get_rect(center=(width // 2, height // 2 - 80))
        screen.blit(loading_text, loading_rect)
        screen.blit(group_text, group_rect)

        # Vẽ progress bar
        pygame.draw.rect(screen, bar_bg_color, (bar_x, bar_y, bar_width, bar_height), border_radius=12)
        fill_width = int(bar_width * progress_percent / 100)
        pygame.draw.rect(screen, bar_fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=12)

        pygame.display.flip()

        # Khi đủ 100%, chuyển qua hiệu ứng fade
        if progress_percent >= 100 or elapsed >= max_duration:
            fade_out(screen, clock)
            running = False

def fade_out(screen, clock, speed=10):
    """Hiệu ứng fade-out mượt"""
    fade_surface = pygame.Surface(screen.get_size()).convert_alpha()
    for alpha in range(0, 256, speed):
        fade_surface.fill((0, 0, 0, alpha))  # alpha từ 0 -> 255
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
