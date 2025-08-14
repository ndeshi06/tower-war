import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': [
        'pygame', 
        'random', 
        'math', 
        'typing',
        'enum',
        'os',
        'sys',
        'json'
    ],
    'excludes': [
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'urllib',
        'xml',
        'pydoc',
        'doctest',
        'argparse',
        'difflib',
        'pdb',
        'profile',
        'pstats',
        'trace',
        'OpenGL',
        'numpy',
        'psutil'
    ],
    'include_files': [
        ('animations/', 'animations/'),
        ('images/', 'images/'),
        ('sounds/', 'sounds/'),
        ('src/', 'src/'),
    ],
    'optimize': 2,
    'silent_level': 1,  # Reduce warnings output
}

# GUI applications require a different base on Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        'main.py',
        base=base,
        target_name='TowerWar.exe',
        icon='images/icon.ico'
    )
]

setup(
    name='Tower War',
    version='1.0.0',
    author='Group 6',
    description='A strategy tower defense game built with pygame',
    long_description='Tower War is an engaging strategy game where players manage towers and troops to defend against enemies.',
    options={'build_exe': build_options},
    executables=executables
)
