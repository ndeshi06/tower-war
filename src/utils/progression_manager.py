import json
import os

class ProgressionManager:
    def __init__(self, save_path=None):
        if save_path is None:
            from .path_utils import get_save_path
            save_path = get_save_path()
        self.save_path = save_path

    def save(self, data):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.save_path):
            return None
        with open(self.save_path, 'r', encoding='utf-8') as f:
            return json.load(f)
