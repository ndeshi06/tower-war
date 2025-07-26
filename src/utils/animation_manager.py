import pygame
import os

class AnimationManager:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.cache = {}

    def load_animation(self, folder, prefix, count, size=None):
        key = (folder, prefix, count, size)
        if key in self.cache:
            return self.cache[key]
        frames = []
        for i in range(1, count+1):
            filename = f"{prefix} ({i}).png"
            path = os.path.join(self.base_folder, folder, filename)
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            frames.append(img)
        self.cache[key] = frames
        return frames

    def get_cat_run(self, size=None):
        return self.load_animation('cat', 'Run', 8, size)
    def get_cat_dead(self, size=None):
        return self.load_animation('cat', 'Dead', 10, size)
    def get_dog_run(self, size=None):
        return self.load_animation('dog', 'Run', 8, size)
    def get_dog_dead(self, size=None):
        return self.load_animation('dog', 'Dead', 10, size)
