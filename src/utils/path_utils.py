"""
Path utilities for handling different paths in script vs executable mode
"""
import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller/cx_freeze
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Check if we're running as cx_freeze executable
        if getattr(sys, 'frozen', False):
            # cx_freeze executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Normal Python script
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, relative_path)

def get_images_path():
    """Get path to images folder"""
    return get_resource_path('images')

def get_sounds_path():
    """Get path to sounds folder"""
    return get_resource_path('sounds')

def get_animations_path():
    """Get path to animations folder"""
    return get_resource_path('animations')

def get_save_path():
    """Get path for save files - should be in user's directory, not in executable folder"""
    if getattr(sys, 'frozen', False):
        # For executable, save in user's AppData or Documents
        try:
            import os
            save_dir = os.path.join(os.path.expanduser("~"), "TowerWar")
            os.makedirs(save_dir, exist_ok=True)
            return os.path.join(save_dir, "progression_save.json")
        except:
            # Fallback to executable directory
            return os.path.join(os.path.dirname(sys.executable), "progression_save.json")
    else:
        # For script mode, save in project directory
        return get_resource_path('progression_save.json')
