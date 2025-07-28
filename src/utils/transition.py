import pygame

def fade_out(screen, clock, speed=10, color=(0, 0, 0)):
    """Hiệu ứng fade màn hình thành màu `color` (mặc định: đen)"""
    fade_surface = pygame.Surface(screen.get_size()).convert_alpha()
    for alpha in range(0, 256, speed):
        fade_surface.fill((*color, alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def fade_in(screen, clock, speed=10, color=(0, 0, 0)):
    """Fade từ màu `color` (mặc định: đen) → hiện màn hình"""
    fade_surface = pygame.Surface(screen.get_size()).convert_alpha()
    for alpha in reversed(range(0, 256, speed)):
        fade_surface.fill((*color, alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
